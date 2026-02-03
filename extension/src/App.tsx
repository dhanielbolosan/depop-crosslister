import { useState } from 'react'
import { Sun, Moon } from 'lucide-react'
import './App.css'

function App() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [activeTab, setActiveTab] = useState<'download' | 'upload'>('download');
  const [selectedPlatform, setSelectedPlatform] = useState<string>('Depop');
  const [username, setUsername] = useState('');

  const handleSubmit = () => {
    if (!username.trim()) {
      console.error('Username is required');
      return;
    }

    const payload = {
      action: activeTab,
      platform: selectedPlatform.toLowerCase(),
      username: username
    };

    chrome.runtime.sendMessage(payload, (response) => {
      if (chrome.runtime.lastError) {
        console.error('Communication Error:', chrome.runtime.lastError.message);
        alert("Error: Could not connect to extension background.");
        return;
      }

      if (response?.error) {
        console.error('Task Failed:', response.error);
        alert(`Error: ${response.error}`);
        return;
      }

      console.log('Success:', response);
    });
  };

  const handleViewData = () => {
    console.log("View Data");
    // TODO: open data view
  };

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <div className={`app-container ${theme}`}>
      <header className="header-container">
        <h1 className="app-title">e-crosslister</h1>
        <button className="theme-toggle" title="Toggle Theme" onClick={toggleTheme}>
          {theme === 'light' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </header>

      <div className="tabs-container">
        <button
          className={activeTab === 'download' ? 'tab-button active' : 'tab-button'}
          onClick={() => setActiveTab('download')}
        >
          Download
        </button>
        <button
          className={activeTab === 'upload' ? 'tab-button active' : 'tab-button'}
          onClick={() => setActiveTab('upload')}
        >
          Upload
        </button>
      </div>

      <div className="content-area">
        <div className="platforms-col">
          <button
            className={selectedPlatform === 'Depop' ? 'platform-button active' : 'platform-button'}
            onClick={() => setSelectedPlatform('Depop')}
          >
            Depop
          </button>
          <button
            className={selectedPlatform === 'Vinted' ? 'platform-button active' : 'platform-button'}
            onClick={() => setSelectedPlatform('Vinted')}
          >
            Vinted
          </button>
          {/*
          
          <button
            className={selectedPlatform === 'FB Marketplace' ? 'platform-button active' : 'platform-button'}
            onClick={() => setSelectedPlatform('FB Marketplace')}
          >
            FB Marketplace
          </button>

          <button
            className={selectedPlatform === 'eBay' ? 'platform-button active' : 'platform-button'}
            onClick={() => setSelectedPlatform('eBay')}
          >
            eBay
          </button>
          */}
        </div>

        <div className="actions-col">
          <input
            type="text"
            className="text-input"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <button className="action-button" onClick={handleSubmit}>
            Start {activeTab === 'download' ? 'Downloading' : 'Uploading'}
          </button>
        </div>
      </div>

      <footer>
        <button className="footer-button" onClick={handleViewData}>
          View Data
        </button>
      </footer>
    </div>
  )
}

export default App
