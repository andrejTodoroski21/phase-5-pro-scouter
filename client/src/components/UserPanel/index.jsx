import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import login from './Login';
import Signup from './Signup';
import UserDetails from './Userdetails';

const UserPanel = () => {
    return (
        <Router>
            <Switch>
                <Route path="/login" component={login} />
                <Route path="/signup" component={Signup} />
                <Route path="/userdetails" component={UserDetails} />
                <Route path="/" component={login} /> {/* Default route */}
            </Switch>
        </Router>
    );
};

export default UserPanel;
