import { Link } from "react-router-dom";
import './styles/layout.css';
import Login from './components/Login'; 

type LayoutProps = {
	children: React.ReactNode;
};

const Layout = ({ children }: LayoutProps) => {
	return (
		<div>
			<header>
				<div id="title">
					<div id="info-container">
						<h1 className="font-bar">Kerlandrier.cc</h1>
						<p id="description">Prenez soin de vos événements</p>
						<span id="infos-link">
							{" "}
							<Link to="/">Retour au Kerlandrier</Link>{" "}
						</span>
					</div>
					<div className="flex flex-col items-start mt-4 sm:items-center">
						<Login />
					</div>
				</div>
			</header>
			<main>{children}</main>
		</div>
	);
};

export default Layout;
