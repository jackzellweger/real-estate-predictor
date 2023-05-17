document.addEventListener("DOMContentLoaded", function () {
  var insertButton = document.getElementById("insertButton");
  insertButton.addEventListener("click", function () {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      chrome.tabs.executeScript(tabs[0].id, {
        code: "var executedFromPopup = true;",
      });
      chrome.tabs.executeScript(tabs[0].id, { file: "content.js" });
    });
  });
});
