"""Consistent Plotly styling for all dashboard panels."""
import plotly.express as px

PALETTE = ['#137E87', '#5374D9', '#E6AA48', '#C66A73', '#8292A9', '#76B8A6']


def chart(data, x, y, title, kind='bar', color=None, hover=None, percent=False):
    factory = px.line if kind == 'line' else px.bar
    fig = factory(data, x=x, y=y, color=color, title=title,
                  hover_data=hover, color_discrete_sequence=PALETTE,
                  labels={x: x.replace('_', ' ').title(), y: y.replace('_', ' ').title()})
    fig.update_layout(template='plotly_white', height=340, margin=dict(l=15, r=15, t=55, b=25),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(family='Arial', color='#172B45'), title_font_size=17,
                      legend_title_text='', hovermode='x unified' if kind == 'line' else 'closest')
    if percent:
        fig.update_yaxes(tickformat='.0%')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor='#E2E8F0')
    return fig
