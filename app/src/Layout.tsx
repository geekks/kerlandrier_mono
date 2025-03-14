// src/components/Layout.tsx
type LayoutProps = {
  children: React.ReactNode;
};

const Layout = ({ children }: LayoutProps) => {
  return (
    <div>
      <header>
        <div id="title">
          <div id="info-container">
            <h1>Kerlandrier.cc</h1>
            <p id="description">Prenez soin de vos événements</p>
            <span id="infos-link"> <a href="/">Retour au Kerlandrier</a> </span>
          </div>

          <div id="qr-container">
            <img id="qr" src="/kerlandrier_qr.svg" alt="Kerlandrier QR code" />
            <br />
            <span>Contribution<br /> et infos sur le site<br /> kerlandrier.cc</span>
          </div>
        </div>
      </header>
      <main>{children}</main>
    </div>
  );
};

export default Layout;
