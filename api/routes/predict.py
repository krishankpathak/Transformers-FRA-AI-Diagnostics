from fastapi import APIRouter, Request
from api.plotter import generate_all_plots

router=APIRouter()

@router.post("/predict")
async def predict(req:Request):

    data=await req.json()
    freq=data.get("freq",[])
    mag=data.get("mag",[])

    plot1,plot2,plot3,plot4 = generate_all_plots(freq,mag)

    return {
        "FRA_Result":"deformation",
        "FDD_Result":2,
        "Final_Diagnosis":"MODERATE",
        "Explanation":["Deviation detected","Possible fault"],
        "plot1":plot1,
        "plot2":plot2,
        "plot3":plot3,
        "plot4":plot4
    }