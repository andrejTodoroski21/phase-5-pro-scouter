import React from "react";
import { Link } from "react-router-dom";

function Footer(){
    return(
        <div className="footer-container">
            <div className="footer-links">
                <h5>Contact</h5>
                <a href="https://github.com/andrejTodoroski21">Github</a>
                <br></br>
                <a href="https://www.linkedin.com/in/andrej-todoroski-18a2bb214/">LinkedIn</a>
            </div>
            <div className="footer-links">
                <h5>Support</h5>
                <a>Phone: 999-999-9999</a>
                <br></br>
                <a>Email: JohnDoe@yahoo.com</a>
            </div>
            <div className="footer-links">
                <h5>What we're about</h5>
                <a href="/about">About</a>
            </div>
        </div> 
    )
}
export default Footer