import React from "react";
import { Link } from "react-router-dom";

function Footer(){
    return(
        <div className="grid-container">
            <footer>

            <div className="left">
            contact
            {/* <ul> */}
                <a href="https://github.com/andrejTodoroski21">Github</a>
                <br></br>
                <a href="https://www.linkedin.com/in/andrej-todoroski-18a2bb214/">LinkedIn</a>
            {/* </ul> */}
            </div>
            <div className="middle">
            support
            {/* <ul> */}
                <a>Phone: 999-999-9999</a>
                <br></br>
                <a>Email: JohnDoe@yahoo.com</a>
            {/* </ul> */}
            </div>
            <br></br>
            <div className="right">
            {/* <ul> */}
                <Link to="/about">About</Link>
            {/* </ul> */}
            </div>
            </footer>
        </div>
    )
}
export default Footer