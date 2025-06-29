import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import Layout from './Layout';
import Home from './pages/Home';
import DiwarBenn from './pages/DiwarBenn';
import Edito from './pages/Edito';


function App() {
  return (
    <>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/diwarbenn" element={<Layout><DiwarBenn /></Layout>} />
          <Route path="/edito" element={<Layout><Edito /></Layout>} />
        </Routes>
      </Router>
    </>
  );
}

export default App;
