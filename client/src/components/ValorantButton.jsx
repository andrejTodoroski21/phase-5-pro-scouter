// src/components/ValorantButton.jsx
import React from 'react';
import './ValorantButton.css';

const ValorantButton = ({ children, onClick }) => {
    return (
        <button className="valorant-button" onClick={onClick}>
            {children}
        </button>
    );
};

export default ValorantButton;
