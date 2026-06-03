/**
 * PASTE THIS INTO YOUR WORDPRESS SITE
 * (Custom HTML block or in your theme's JS file)
 *
 * Replace API_BASE with your deployed Railway/Render URL
 */

const API_BASE = "https://your-api.railway.app"; // ← CHANGE THIS

document.addEventListener("DOMContentLoaded", function () {
  const convertBtn = document.querySelector("button"); // adjust selector to match your button
  const urlInput = document.querySelector("input[type='text']"); // adjust if needed

  if (!convertBtn || !urlInput) return;

  convertBtn.addEventListener("click", async function () {
    const url = urlInput.value.trim();
    const format = document.querySelector("[data-format].active")?.dataset.format || "mp3";
    const quality = document.querySelector("[data-quality].active")?.dataset.quality || "192";

    if (!url) {
      alert("Please enter a YouTube URL");
      return;
    }

    convertBtn.disabled = true;
    convertBtn.textContent = "Fetching info...";

    try {
      // Step 1: Get video info
      const infoRes = await fetch(`${API_BASE}/info?url=${encodeURIComponent(url)}`);
      const info = await infoRes.json();

      if (info.error) throw new Error(info.error);

      // Update UI with video title/channel (adjust selectors to match your HTML)
      const titleEl = document.querySelector(".video-title");
      const channelEl = document.querySelector(".channel-name");
      if (titleEl) titleEl.textContent = info.title;
      if (channelEl) channelEl.textContent = info.channel;

      convertBtn.textContent = "Downloading...";

      // Step 2: Trigger download
      const downloadUrl = `${API_BASE}/convert?url=${encodeURIComponent(url)}&format=${format}&quality=${quality}`;
      
      // Create a hidden link and click it to start download
      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = `${info.title}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);

      convertBtn.textContent = "✅ Done! Download started";
    } catch (err) {
      alert("Error: " + err.message);
      convertBtn.textContent = "Convert Now";
    } finally {
      convertBtn.disabled = false;
      setTimeout(() => { convertBtn.textContent = "Convert Now"; }, 5000);
    }
  });
});
