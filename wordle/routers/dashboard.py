from fastapi import Depends, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from ..db.database import get_db
from .. import schemas
from sqlalchemy.orm import Session
from ..auth import auth_utils
from typing import Annotated
from .common import templates
import plotly.express as px
import pandas as pd


router = APIRouter(prefix='/dashboard')


def game_stats(user: Annotated[schemas.User, Depends(auth_utils.manager)], db: Annotated[Session, Depends(get_db)]):
    df = pd.DataFrame({"id": [g.id for g in user.games], "points": [g.points for g in user.games], "result": [g.won for g in user.games]})
    winning_perc = df[df['result']].size / df.size if df.size > 0 else 0.0
    df['result'] = df['result'].replace(True, 'won').replace(False, 'lost')
    chart = px.pie(
        data_frame=df,
        names="result",
        height=300,
        width=400
    )
    chart.update_traces(textposition='inside', textinfo='value+label')
    chart.update_layout(
        margin=dict(l=0,r=0,t=0,b=0),
        showlegend=False
    )
    return chart, winning_perc


@router.get("/", response_class=HTMLResponse)
async def show_dashboard(request: Request, user: Annotated[schemas.User, Depends(auth_utils.manager)], db: Annotated[Session, Depends(get_db)]):
    chart, winning_perc = game_stats(db=db, user=user)
    return templates.TemplateResponse(
        request=request, name="dashboard/dashboard.html", context={"user": user, "winning_pie_chart": chart.to_html(full_html=False), "winning_perc": winning_perc}, status_code=200
    )
