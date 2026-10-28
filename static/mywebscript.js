"use strict";

const analyzeButton = document.getElementById("analyzeButton");
const textInput = document.getElementById("textToAnalyze");
const responsePanel = document.getElementById("responsePanel");
const responseText = document.getElementById("system_response");

async function RunSentimentAnalysis() {
  const text = textInput.value;
  responsePanel.hidden = false;
  responsePanel.classList.remove("error");
  analyzeButton.disabled = true;
  responseText.textContent = "Analyzing...";

  try {
    const url = "/emotionDetector?textToAnalyze=" + encodeURIComponent(text);
    const response = await fetch(url);
    const message = await response.text();
    if (!response.ok) {
      responsePanel.classList.add("error");
    }
    responseText.textContent = message;
  } catch (error) {
    responsePanel.classList.add("error");
    responseText.textContent = "Network error. Please try again later.";
  } finally {
    analyzeButton.disabled = false;
  }
}

analyzeButton.addEventListener("click", RunSentimentAnalysis);
