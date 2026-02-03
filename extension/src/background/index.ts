chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  const { action, platform } = message;
  console.log(`Background received: ${action} on ${platform}`);

  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const tabId = tabs[0]?.id;
    
    if (!tabId) {
      sendResponse({ success: false, error: 'No active tab found' });
      return;
    }

    chrome.tabs.sendMessage(tabId, message, (response) => {
      if (chrome.runtime.lastError) {
        console.warn("Content script error:", chrome.runtime.lastError.message);
        sendResponse({ 
          success: false, 
          error: "Refused to connect. Are you on the correct website?" 
        });
        return;
      }
      
      console.log('Content script responded:', response);
      sendResponse(response);
    });
  });

  return true; // Keep message channel open
});