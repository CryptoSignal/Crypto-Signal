import React from 'react';

class Navbar extends React.Component {
	constructor(props) {
		super(props);

	}

	render() {
		return (
			<nav>
              <div className="nav-wrapper">
              <a href="#" className="brand-logo">CryptoBot</a>
              </div>
            </nav>
		)
	}

}

export default Navbar;