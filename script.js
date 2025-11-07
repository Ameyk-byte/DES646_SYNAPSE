//  EEL SUPPORT (Python → JS communication)
if (typeof eel !== "undefined") {
  console.log("EEL is connected and ready.");
}

const canvas = document.getElementById('sphereCanvas');
const ctx = canvas.getContext('2d');

// Set canvas dimensions
canvas.width = 500;
canvas.height = 500;

// Sphere properties
const centerX = canvas.width / 2;
const centerY = canvas.height / 2;
const baseRadius = 150;
let amplitude = 0;
let pulseScale = 1;
let pulseDirection = 1;

// Audio setup
let audioContext, analyser, dataArray, source, stream;

// Mic button
const micButton = document.getElementById('micButton');
micButton.addEventListener('click', async () => {
  if (!audioContext) {
    await startAudio();
  }
});

async function startAudio() {
  try {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;
    dataArray = new Uint8Array(analyser.frequencyBinCount);

    // request microphone
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);

    animateSphere();
  } catch (err) {
    console.error('Microphone access error:', err);
  }
}

function animateSphere() {
  requestAnimationFrame(animateSphere);

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  analyser.getByteFrequencyData(dataArray);

  const avgAmplitude = dataArray.reduce((sum, val) => sum + val, 0) / dataArray.length;
  amplitude = avgAmplitude / 10;

  pulseScale += pulseDirection * 0.01;
  if (pulseScale > 1.2 || pulseScale < 0.8) {
    pulseDirection *= -1;
  }

  drawSiriSphere(centerX, centerY, baseRadius, amplitude, pulseScale);
}

function drawSiriSphere(x, y, r, amp, pulse) {
  ctx.beginPath();

  for (let angle = 0; angle < Math.PI * 2; angle += 0.01) {
    const dynamicRadius = r * pulse + Math.sin(angle * 10 + amp) * 10;
    const posX = x + dynamicRadius * Math.cos(angle);
    const posY = y + dynamicRadius * Math.sin(angle);
    if (angle === 0) {
      ctx.moveTo(posX, posY);
    } else {
      ctx.lineTo(posX, posY);
    }
  }

  const gradient = ctx.createRadialGradient(
    x, y, r * pulse * 0.5,
    x, y, r * pulse
  );

  gradient.addColorStop(0, 'rgba(0, 123, 255, 0.8)');
  gradient.addColorStop(1, 'rgba(0, 123, 255, 0)');

  ctx.strokeStyle = gradient;
  ctx.lineWidth = 2;
  ctx.fillStyle = 'rgba(0, 123, 255, 0.2)';
  ctx.fill();
  ctx.stroke();
}

// called by Python when Learning Recommender returns results
eel.expose(updateLearningResources);
function updateLearningResources(resources) {
  const learningBox = document.getElementById("learningBox");
  const list = document.getElementById("learningList");

  if (!resources || resources.length === 0) {
    learningBox.style.display = "none";
    return;
  }

  list.innerHTML = "";

  resources.forEach(r => {
    const item = document.createElement("div");
    item.className = "learning-item";
    item.innerHTML = `
      <b>${r.title}</b> (${r.level})<br>
      ${r.type} • ~${r.duration_min} min<br>
      <a href="${r.url}" target="_blank">Open</a>
    `;
    list.appendChild(item);
  });

  learningBox.style.display = "block";
}
