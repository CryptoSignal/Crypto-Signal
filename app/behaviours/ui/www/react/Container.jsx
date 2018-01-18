import React from 'react';

import Navbar from './Navbar.jsx';
import Dashboard from './Dashboard.jsx';

class Container extends React.Component {
	constructor(props) {
		super(props);
	}

	render() {
		return (
			<div id="container">
			    <Navbar />
			    <Dashboard />
			</div>
		)
	}
}

export default Container;