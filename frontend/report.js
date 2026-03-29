let lastResult = null;

function parseCSVUniversal(text) {

    const lines = text.split("\n");
    let freq = [], mag = [];

    lines.forEach(line => {
        const parts = line.split(/,|\t|;/);

        const nums = parts.map(x => parseFloat(x)).filter(x => !isNaN(x));

        if (nums.length >= 2) {
            freq.push(nums[0]);
            mag.push(nums[1]);
        }
    });

    return { freq, mag };
}

function extractFeatures(freq, mag) {

    const mean = mag.reduce((a,b)=>a+b,0)/mag.length;

    return {
        mean_mag: mean,
        std_mag: 10,
        min_mag: Math.min(...mag),
        max_mag: Math.max(...mag),
        low_mean: mean,
        mid_mean: mean,
        high_mean: mean,
        peak_freq: freq[0],
        peak_mag: Math.max(...mag),
        slope: 0
    };
}

function autoGenerateGas(f) {
    return {
        H2: Math.abs(f.mean_mag * 50),
        CO: 200,
        C2H4: 100,
        C2H2: 20,
        rul: 500
    };
}

async function uploadCSV() {

    const loader = document.getElementById("loader");
    loader.classList.remove("hidden");

    const file = document.getElementById("csvFile").files[0];

    if (!file) {
        alert("Upload file");
        loader.classList.add("hidden");
        return;
    }

    const text = await file.text();

    const parsed = parseCSVUniversal(text);

    if (parsed.freq.length < 5) {
        alert("Invalid CSV");
        loader.classList.add("hidden");
        return;
    }

    plotComparison(parsed.freq, parsed.mag);

    const features = extractFeatures(parsed.freq, parsed.mag);
    const gas = autoGenerateGas(features);

    const res = await fetch("http://127.0.0.1:8000/api/predict", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({fra_features: features, gas_data: gas})
    });

    const data = await res.json();
    lastResult = data;

    updateUI(data);

    loader.classList.add("hidden");
}

function updateUI(data) {

    document.getElementById("fraResult").innerText = data.FRA_Result;
    document.getElementById("fddResult").innerText = data.FDD_Result;
    document.getElementById("finalResult").innerText = data.Final_Diagnosis;

    const gauge = document.getElementById("gaugeFill");
    gauge.style.width = (data.FDD_Result * 25) + "%";

    const list = document.getElementById("explanation");
    list.innerHTML = "";

    if (data.Explanation) {
        data.Explanation.forEach(e => {
            const li = document.createElement("li");
            li.innerText = e;
            list.appendChild(li);
        });
    }
}