chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Vinted Script Received:', message);

  if (message.action === 'download') {
    console.log('Starting Vinted Download for:', message.username);
    sendResponse({ success: true, message: 'Vinted Download Started' });
  } 
  else if (message.action === 'upload') {
    console.log('Starting Vinted Upload for:', message.username);
    sendResponse({ success: true, message: 'Vinted Upload Started' });
  }

  return true;
});