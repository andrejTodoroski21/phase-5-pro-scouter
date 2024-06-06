import React, { useEffect, useState } from 'react';

const UserDetails = () => {
    const [user, setUser] = useState(null);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchUserDetails = async () => {
            try {
                const response = await fetch('/api/userdetails');
                if (response.ok) {
                    const data = await response.json();
                    setUser(data);
                } else {
                    setError('Error fetching user details');
                }
            } catch (err) {
                setError('Error fetching user details');
            }
        };

        fetchUserDetails();
    }, []);

    if (error) {
        return <p>{error}</p>;
    }

    if (!user) {
        return <p>Loading...</p>;
    }

    return (
        <div>
            <h2>User Details</h2>
            <p>Username: {user.username}</p>
            <p>First Name: {user.first_name}</p>
            <p>Last Name: {user.last_name}</p>
        </div>
    );
};

export default UserDetails;
