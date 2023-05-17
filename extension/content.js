if (typeof executedFromPopup !== "undefined") {
  var helloWorldDiv = document.createElement("div");
  helloWorldDiv.innerText = "Hello World";
  helloWorldDiv.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: yellow;
        text-align: center;
        font-size: 20px;
        padding: 10px;
        z-index: 9999;
      `;

  document.body.prepend(helloWorldDiv);
}
