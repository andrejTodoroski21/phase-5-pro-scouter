"""Where uploaded clips live.

Two backends behind one interface. Local disk is the default so the app runs
with no credentials at all; R2 takes over as soon as its settings are present.
Nothing above this module knows which is in use.

R2 speaks the S3 API, so boto3 drives it. The only unusual parts are the
account-scoped endpoint and that R2 ignores regions, hence ``auto``.
"""
import mimetypes
import os
from pathlib import Path

from flask import current_app

R2_SETTINGS = ('R2_ACCOUNT_ID', 'R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY', 'R2_BUCKET')


class StorageError(Exception):
    pass


class Storage:
    """Interface. ``key`` is a bucket-relative path like ``clips/ab12.mp4``."""

    def save(self, key, stream, content_type=None):
        raise NotImplementedError

    def delete(self, key):
        raise NotImplementedError

    def public_url(self, key):
        raise NotImplementedError


class LocalStorage(Storage):
    """Writes under ``MEDIA_ROOT`` and serves through the app's /media route."""

    def __init__(self, root, base_url='/media'):
        self.root = Path(root)
        self.base_url = base_url.rstrip('/')
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key):
        # Resolve and confirm the result is still inside the root, so a key
        # containing ../ cannot escape it.
        target = (self.root / key).resolve()
        if not str(target).startswith(str(self.root.resolve())):
            raise StorageError('key escapes the media root')
        return target

    def save(self, key, stream, content_type=None):
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as out:
            while chunk := stream.read(1024 * 256):
                out.write(chunk)

    def delete(self, key):
        try:
            self._path(key).unlink()
        except FileNotFoundError:
            pass

    def public_url(self, key):
        return f'{self.base_url}/{key}'


class R2Storage(Storage):
    def __init__(self, account_id, access_key, secret_key, bucket, public_base_url):
        import boto3
        from botocore.config import Config

        self.bucket = bucket
        self.public_base_url = (public_base_url or '').rstrip('/')
        self.client = boto3.client(
            's3',
            endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            # R2 has no regions, but the S3 client insists on one.
            region_name='auto',
            config=Config(signature_version='s3v4', retries={'max_attempts': 3}),
        )

    def save(self, key, stream, content_type=None):
        content_type = content_type or mimetypes.guess_type(key)[0] or 'application/octet-stream'
        self.client.upload_fileobj(
            stream, self.bucket, key,
            ExtraArgs={
                'ContentType': content_type,
                # Clips are immutable once written; the key carries a random id.
                'CacheControl': 'public, max-age=31536000, immutable',
            },
        )

    def delete(self, key):
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def public_url(self, key):
        if not self.public_base_url:
            raise StorageError('R2_PUBLIC_BASE_URL is not set')
        return f'{self.public_base_url}/{key}'


def configure(app):
    """Pick a backend from config and stash it on the app."""
    if all(app.config.get(name) for name in R2_SETTINGS):
        app.extensions['storage'] = R2Storage(
            account_id=app.config['R2_ACCOUNT_ID'],
            access_key=app.config['R2_ACCESS_KEY_ID'],
            secret_key=app.config['R2_SECRET_ACCESS_KEY'],
            bucket=app.config['R2_BUCKET'],
            public_base_url=app.config.get('R2_PUBLIC_BASE_URL'),
        )
        app.logger.info('Clip storage: Cloudflare R2 (%s)', app.config['R2_BUCKET'])
    else:
        app.extensions['storage'] = LocalStorage(app.config['MEDIA_ROOT'])
        missing = [n for n in R2_SETTINGS if not app.config.get(n)]
        app.logger.info('Clip storage: local disk (R2 not configured: %s)', ', '.join(missing))


def get():
    return current_app.extensions['storage']


def env_settings():
    """R2 settings read from the environment, for create_app."""
    return {
        name: os.environ.get(name) for name in
        R2_SETTINGS + ('R2_PUBLIC_BASE_URL',)
    }
