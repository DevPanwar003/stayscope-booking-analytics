"""Consistent Plotly styling for all dashboard panels."""
import plotly.express as px

PALETTE = ['#137E87', '#5374D9', '#E6AA48', '#C66A73', '#8292A9', '#76B8A6']


def chart(data, x, y, title, kind='bar', color=None, hover=None, percent=False,
          confidence=False, benchmark=None):
    data = data.copy()
    hover = dict(hover) if isinstance(hover, dict) else {name: True for name in (hover or [])}
    if percent:
        hover[y] = ':.1%'
    elif y in {'booking_value', 'cancelled_booking_value', 'markup'}:
        hover[y] = ':,.2f'
    errors = {}
    if confidence:
        data['_upper_error'] = (data.ci_upper - data[y]).clip(lower=0)
        data['_lower_error'] = (data[y] - data.ci_lower).clip(lower=0)
        errors = {'error_y': '_upper_error', 'error_y_minus': '_lower_error'}
    factory = px.line if kind == 'line' else px.bar
    fig = factory(data, x=x, y=y, color=color, title=title,
                  hover_data=hover, color_discrete_sequence=PALETTE,
                  labels={x: x.replace('_', ' ').title(), y: y.replace('_', ' ').title(),
                          'ci_lower': '95% Wilson lower', 'ci_upper': '95% Wilson upper',
                          'difference_pp': 'Difference (pp)'}, **errors)
    fig.update_layout(template='plotly_white', height=340, margin=dict(l=15, r=15, t=55, b=25),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(family='Arial', color='#172B45'), title_font_size=17,
                      legend_title_text='', hovermode='x unified' if kind == 'line' else 'closest')
    if percent:
        fig.update_yaxes(tickformat='.0%')
        fig.update_yaxes(range=[0, 1.08] if confidence else None)
    if benchmark is not None:
        fig.add_hline(y=benchmark, line_dash='dot', line_color='#172B45',
                      annotation_text=f'Selection overall {benchmark:.1%}', annotation_position='top left')
    fig.update_layout(hoverlabel=dict(bgcolor='white', font_color='#172B45'),
                      legend=dict(orientation='h', y=-0.25), bargap=0.3)
    fig.update_xaxes(showgrid=False, automargin=True)
    fig.update_yaxes(gridcolor='#E2E8F0', automargin=True)
    return fig
