import React from 'react';
import Login from './Login';
import Signup from './Signup';
import UserDetails from './Userdetails';

const UserPanel = ({currentUser, setCurrentUser}) => {
    if(!currentUser){

        
        return (
            <div>
                <Signup setCurrentUser={setCurrentUser}></Signup>
                <Login setCurrentUser={setCurrentUser}></Login>
            </div>
    )
}   else{
        return (
            <div>
                <UserDetails user={currentUser}></UserDetails>
            </div>
        )
    }
};

export default UserPanel;
