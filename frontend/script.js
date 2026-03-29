let fraChart=null;

function parseCSV(text){
    const lines=text.split("\n");
    let f=[],m=[];
    for(let i=1;i<lines.length;i++){
        const p=lines[i].split(/,|\t|;/);
        let x=parseFloat(p[0]), y=parseFloat(p[1]);
        if(!isNaN(x)&&!isNaN(y)){f.push(x);m.push(y);}
    }
    return {f,m};
}

function plot(freq,mag){
    const ctx=document.getElementById("fraChart");

    const data=freq.map((x,i)=>({x:x,y:mag[i]}));

    if(fraChart){
        fraChart.data.datasets[0].data=data;
        fraChart.update();
        return;
    }

    fraChart=new Chart(ctx,{
        type:"line",
        data:{datasets:[{label:"FRA",data:data,borderColor:"#38bdf8",pointRadius:0}]},
        options:{
            parsing:false,
            scales:{x:{type:"logarithmic"},y:{}}
        }
    });
}

async function uploadCSV(){
    const file=document.getElementById("csvFile").files[0];
    if(!file){ alert("Choose a CSV file first."); return; }
    const text=await file.text();

    let d=parseCSV(text);

    plot(d.f,d.m);

    const res=await fetch("http://127.0.0.1:8000/api/predict",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({freq:d.f,mag:d.m})
    });

    const data=await res.json();

    document.getElementById("fraResult").innerText=data.FRA_Result;
    document.getElementById("fddResult").innerText=data.FDD_Result;
    document.getElementById("finalResult").innerText=data.Final_Diagnosis;

    document.getElementById("plot1").src="data:image/png;base64,"+data.plot1;
    document.getElementById("plot2").src="data:image/png;base64,"+data.plot2;
    document.getElementById("plot3").src="data:image/png;base64,"+data.plot3;

    let list=document.getElementById("explanation");
    list.innerHTML="";
    (data.Explanation || []).forEach(e=>{
        let li=document.createElement("li");
        li.innerText=e;
        list.appendChild(li);
    });

    const g = document.getElementById("gaugeFill");
    if (g) {
        const t = String(data.Final_Diagnosis || "").toUpperCase();
        const w = t.includes("CRITICAL") ? 92 : t.includes("HIGH") || t.includes("MODERATE") ? 65 : t.includes("WARNING") ? 45 : 22;
        g.style.width = w + "%";
    }
}

function generatePDF(){
    const { jsPDF } = window.jspdf;
    let doc=new jsPDF();

    doc.text("FRA Diagnostic Report",10,10);
    doc.text("Final: "+document.getElementById("finalResult").innerText,10,20);

    doc.save("report.pdf");
}