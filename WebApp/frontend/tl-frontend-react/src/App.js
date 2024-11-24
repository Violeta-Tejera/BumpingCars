import logo from './logo.svg';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;


// -------------------------------------

// // import logo from './logo.svg';
// // import './App.css';
// import React from 'react';

// // import { Box } from '@mui/material';
// // import Header from './components/chat_page/Header';
// // import Sidebar from './components/chat_page/Sidebar';
// // import ChatArea from './components/chat_page/ChatArea';

// // import ChatPage from './components/chat_page/ChatPage';
// // import ChatPage from './components/chat_page/MainPage';
// import MainPage from './components/MainPage';

// function App() {
//   return (
//     // <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
//     //   <Header />
//     //   <Box sx={{ display: 'flex', flexGrow: 1, overflow: 'hidden' }}>
//     //     <Sidebar />
//     //     <ChatArea />
//     //   </Box>
//     // </Box>

//     // <ChatPage />
//     <MainPage />
//   );
// }

// export default App;

// -------------------------------------

// App.js (nuevo archivo principal)
// import React from 'react';
// import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
// import MainLayout from './components/main/MainLayout';
// import ProjectsPage from './pages/ProjectsPage';
// import ChatPage from './pages/ChatPage';
// import CodeEditorPage from './pages/CodeEditorPage';

// function App() {
//   return (
//     <BrowserRouter>
//       <Routes>
//         <Route path="/" element={<MainLayout />}>
//           <Route index element={<Navigate to="/projects" replace />} />
//           <Route path="projects" element={<ProjectsPage />} />
//           <Route path="chat/:chatbotSlug" element={<ChatPage />} />
//           <Route path="editor/:chatbotSlug" element={<CodeEditorPage />} />
//           <Route path="*" element={<Navigate to="/projects" replace />} />
//         </Route>
//       </Routes>
//     </BrowserRouter>
//   );
// }

// export default App;
