import { Link } from "react-router-dom";

const DiwarBenn = () => {
	return (
		<section>
			<div id="abonnement">
				<h3>Vous voulez ajouter le Kerlandrier à votre agenda ?</h3>
				<br />
				<p>
					Rendez-vous sur la{" "}
					<a href="https://openagenda.com/fr/kerlandrier">
						page OpenAgenda du Kerlandrier
					</a>
					,
				</p>
				<p>
					Cliquez sur <i>Exporter</i>, et choisissez votre agenda{" "}
					<i>(Google Agenda, Outlook, iCal, etc.)</i>.
				</p>
				<div
					style={{
						display: "flex",
						justifyContent: "center",
						alignItems: "end",
					}}
				>
					Ou utilisez les liens suivants : &nbsp;
					<a
						href="https://openagenda.com/agendas/44891982/events.v2.ics?relative%5B0%5D=current&relative%5B1%5D=upcoming"
						title="Flux iCal"
						id="icon-link-ical"
					>
						<div id="icon-ical" />
					</a>
					<a
						href="https://openagenda.com/agendas/44891982/events.v2.rss?relative%5B0%5D=current&relative%5B1%5D=upcoming"
						title="Flux RSS"
						id="icon-link-rss"
					>
						<div id="icon-rss" />
					</a>
				</div>
			</div>
			<div id="contribution">
				<h3>Le Kerlandrier est un projet collaboratif</h3>
				<br />
				<p>
					<i>Le projet dit oui à votre assistance si vous...</i>
				</p>

				<ul>
					<li>...êtes au courant des bons plans du territoire,</li>
					<li>...parcourez les internets pour en extraire des pépites,</li>
					<li>...collez des affiches à vos heures perdues,</li>
					<li>
						...souhaitez{" "}
						<a href="https://openagenda.com/kerlandrier/contribute">
							ajouter un évènement non présent
						</a>{" "}
						dans la{" "}
						<a href="https://openagenda.com/fr/kerlandrier">
							liste des événements
						</a>{" "}
						(nécessite de créer un compte OpenAgenda)
					</li>
					<li>
						...possédez un agenda type Google Agenda que vous pouvez rendre
						public.
					</li>
				</ul>
				<br />
				<p>
					{" "}
					Site web : <Link to="/">kerlandrier.cc</Link> - Contact : contact [at]
					kerlandrier.cc
				</p>
				<br />
				<h3 style={{ textAlign: "center" }}>Rejoignez-nous</h3>
				<br />
				<img id="join-us" src="/join_us_pop_teal.png" alt="Join us" />
			</div>
		</section>
	);
};

export default DiwarBenn;
