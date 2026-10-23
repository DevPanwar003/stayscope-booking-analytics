"""StayScope — a local business intelligence and booking analytics platform."""
from pathlib import Path
from hashlib import sha256
import sqlite3

import pandas as pd
import streamlit as st

from src.analytics import FORMULAS, breakdown, filter_bookings, insights, kpis, monthly
from src.charts import chart
from src.database import datasets, initialize, load_dataset, quality_report, reset_demo, save_dataset
from src.exports import csv_bytes, excel_bytes, summary_frame
from src.validation import DataError, read_upload, validate

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'data' / 'bookings.db'
SAMPLE = ROOT / 'data' / 'sample_hotel_bookings.csv'

st.set_page_config(page_title='StayScope | Booking intelligence', page_icon='🏨', layout='wide')
st.markdown('''<style>
    .stApp {background:#F5F7FB;}
    [data-testid="stSidebar"] {background:#13243B;}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] .stMarkdown p {color:#EAF0F8;}
    [data-testid="stMetric"] {background:white;border:1px solid #E0E7EF;border-radius:14px;padding:18px;}
    [data-testid="stMetricValue"] {font-size:1.65rem;color:#13243B;}
    .block-container {padding-top:2rem;max-width:1500px;}
    h1 {letter-spacing:-1.3px;} h2,h3 {letter-spacing:-.4px;}
    [data-testid="stPlotlyChart"] {background:white;border-radius:14px;border:1px solid #E0E7EF;}
    @media(max-width:1400px) {
      [data-testid="stHorizontalBlock"] {flex-wrap:wrap;}
      [data-testid="stColumn"] {min-width:min(100%,240px);flex:1 1 calc(50% - 1rem);}
    }
    @media(max-width:700px) {.block-container {padding:4rem 1rem 1rem;} [data-testid="stMetric"] {padding:12px;}}
</style>''', unsafe_allow_html=True)


def seed_demo():
    return save_dataset(DB, validate(read_upload(SAMPLE.read_bytes(), SAMPLE.name)),
                        'Synthetic hotel demonstration', is_demo=True)


def quality_panel(summary, issues, rejected):
    cols = st.columns(4)
    for column, label, key in zip(cols, ['Source rows', 'Accepted', 'Quarantined', 'Duplicates'],
                                  ['input_rows', 'accepted_rows', 'quarantined_rows', 'duplicate_rows']):
        column.metric(label, summary[key])
    if summary['issue_count']:
        st.warning(f"{summary['issue_count']} quality issues recorded. Review decisions before using the data.")
    else:
        st.success('No row-level validation issues detected.')
    if summary.get('missing_optional_columns'):
        st.info('Optional columns absent: ' + ', '.join(summary['missing_optional_columns']))
    if summary.get('ignored_columns'):
        st.info('Columns excluded from storage and analytics: ' + ', '.join(summary['ignored_columns']))
    if not issues.empty:
        st.dataframe(issues, hide_index=True, width='stretch')
        st.download_button('Download quality decisions', csv_bytes(issues), 'quality_decisions.csv', 'text/csv')
    if not rejected.empty:
        st.caption('Quarantined canonical records; use source_row to inspect raw values in your original file.')
        st.dataframe(rejected, hide_index=True, width='stretch')
        st.download_button('Download quarantined records', csv_bytes(rejected), 'quarantined.csv', 'text/csv')


def import_page():
    st.title('Bring your bookings into focus')
    st.caption('IMPORT & QUALITY  /  Review first. Save a separate dataset when ready.')
    if 'import_feedback' in st.session_state:
        st.success(st.session_state.pop('import_feedback'))
    with st.expander('File requirements and cleaning rules', expanded=True):
        st.markdown('Required: `booking_id`, `booking_date`, `status`, `booking_value`. '
                    'Dates must use ISO format (`YYYY-MM-DD`). Optional: `city`, `property`, '
                    '`channel`, `room_type`, `star_rating`, `cost`. Excel reads the first sheet.')
        st.write('Invalid required values are quarantined; optional numeric errors become missing. '
                 'Exact duplicates keep one record; conflicting booking IDs quarantine all versions. '
                 'Unrecognized columns are excluded to reduce accidental personal-data exposure. '
                 'Keep your original file: the database stores canonical data and quality decisions, not the original upload.')
    st.download_button('Download synthetic sample CSV', SAMPLE.read_bytes(), SAMPLE.name, 'text/csv')
    upload = st.file_uploader('Upload booking records', type=['csv', 'xlsx'])
    currency = st.selectbox('Dataset currency (all amounts must use one currency)', ['INR', 'USD', 'EUR', 'GBP', 'Other / units'])
    if upload:
        try:
            with st.spinner('Reading and validating booking records…'):
                result = validate(read_upload(upload.getvalue(), upload.name))
            quality_panel(result.summary, result.issues, result.rejected)
            with st.expander('Preview accepted records'):
                st.dataframe(result.accepted.head(100), hide_index=True)
            review_key = sha256(upload.getvalue() + currency.encode()).hexdigest()
            agreed = st.checkbox('I reviewed the quality decisions and confirm this file uses the selected currency.',
                                 key=f'review_{review_key}')
            if st.button('Save reviewed dataset', type='primary', disabled=not agreed or result.accepted.empty):
                dataset_id, created = save_dataset(DB, result, upload.name, currency)
                st.session_state['import_feedback'] = (f'Dataset #{dataset_id} saved. Select it in the sidebar.' if created
                                                      else f'Already imported as dataset #{dataset_id}; no records added.')
                st.rerun()
        except DataError as exc:
            st.error(str(exc))
    st.divider()
    st.subheader('Demo management')
    st.write('Reset removes only the synthetic demo snapshot and restores the supplied sample. Uploaded datasets are preserved.')
    confirmation = st.text_input('Type RESET DEMO to confirm removal of demo data')
    if st.button('Reset synthetic demo', disabled=confirmation != 'RESET DEMO'):
        try:
            replacement = validate(read_upload(SAMPLE.read_bytes(), SAMPLE.name))
            if replacement.accepted.empty:
                raise DataError('The demo sample contains no valid bookings; existing data was preserved.')
            reset_demo(DB, confirmation, replacement=replacement)
            st.session_state['import_feedback'] = 'Synthetic demo restored. Uploaded datasets were preserved.'
            st.rerun()
        except DataError as exc:
            st.error(f'Demo reset cancelled: {exc}')


def render_chart(*args, **kwargs):
    st.plotly_chart(chart(*args, **kwargs), width='stretch', config={'displaylogo': False})


def overview(data, currency):
    st.title('A clearer view of every booking')
    st.caption('EXECUTIVE OVERVIEW  /  Booking performance, without the guesswork')
    metrics = kpis(data)
    for offset in [0, 4]:
        for column, (label, value) in zip(st.columns(4), list(metrics.items())[offset:offset + 4]):
            display = 'N/A' if value is None else f'{value:.1%}' if label == 'Cancellation rate' else (
                f'{value:,.0f}' if 'bookings' in label else f'{value:,.2f}')
            column.metric(label, display, help=FORMULAS[label])
    st.caption(f'Amounts in {currency}. Retained value includes Confirmed + Completed only. '
               'Markup is selling value minus supplier cost, before overheads. Neither measure is recognized revenue or cash collected.')
    if data.empty:
        st.info('No bookings match these filters. Broaden your selection to see charts.')
        return
    render_chart(monthly(data), 'period', 'booking_value', f'Booking value over time · {currency}', kind='line', hover=['bookings'])
    left, right = st.columns(2)
    with left:
        render_chart(breakdown(data, 'channel'), 'channel', 'bookings', 'Where bookings originate')
        render_chart(breakdown(data, 'room_type'), 'room_type', 'booking_value', f'Room performance · {currency}', hover=['bookings'])
        render_chart(breakdown(data, 'status'), 'status', 'bookings', 'Booking status', color='status')
    with right:
        render_chart(breakdown(data, 'channel'), 'channel', 'cancellation_rate', 'Cancellation rate by channel',
                     hover=['bookings', 'cancelled'], percent=True)
        ratings = data.copy()
        ratings['star_rating'] = ratings.star_rating.map(lambda x: 'Unknown' if pd.isna(x) else f'{int(x)} stars')
        render_chart(breakdown(ratings, 'star_rating'), 'star_rating', 'booking_value', f'Property rating · {currency}', hover=['bookings'])
        render_chart(breakdown(data, 'city').sort_values('booking_value', ascending=False).head(10),
                     'city', 'booking_value', f'Top cities · {currency}', hover=['bookings'])
    st.subheader('Property performance')
    st.dataframe(breakdown(data, 'property').sort_values('booking_value', ascending=False), hide_index=True, width='stretch')
    retained = data[data.status.isin(['Confirmed', 'Completed'])]
    if metrics['Retained markup'] is not None:
        profits = retained.assign(markup=retained.booking_value - retained.cost).groupby('channel', as_index=False).markup.sum()
        render_chart(profits, 'channel', 'markup', f'Retained markup by channel · {currency}')
    else:
        st.info('Markup requires complete cost data for all retained bookings in this selection.')
    st.subheader('What the data says')
    for item in insights(data):
        st.info(item)
    with st.expander('KPI dictionary & interpretation'):
        st.dataframe(pd.DataFrame(FORMULAS.items(), columns=['KPI', 'Formula']), hide_index=True, width='stretch')


def comparisons(data):
    st.title('Explore cancellation patterns')
    st.write('Compare rates with their sample sizes. These associations do not establish causation.')
    if data.empty:
        st.info('No bookings match these filters.')
        return
    if data.status.nunique() == 1:
        st.warning('Only one booking status is present. Select all statuses for a meaningful cancellation comparison.')
    dimension = st.selectbox('Compare by', ['channel', 'room_type', 'city', 'booking_period'])
    minimum = st.slider('Minimum group size to highlight', 5, 100, 20)
    work = data.assign(booking_period=data.booking_date.dt.to_period('M').astype(str))
    groups = breakdown(work, dimension)
    groups['sample_note'] = groups.bookings.map(lambda n: 'Small sample — interpret cautiously' if n < minimum else 'Meets selected threshold')
    render_chart(groups, dimension, 'cancellation_rate', 'Cancellation rate and sample size',
                 hover=['bookings', 'cancelled', 'sample_note'], percent=True)
    st.dataframe(groups, hide_index=True, width='stretch', column_config={
        'cancellation_rate': st.column_config.NumberColumn('Cancellation rate (fraction)', format='%.3f')})
    st.caption('All groups remain visible. A sample threshold is a caution, not a statistical significance test. '
               'Rates may reflect season, customer mix, lead time or other unmeasured factors.')


def explorer(data, full, dataset_id):
    st.title('Know the data behind the numbers')
    st.caption(f'Filtered records: {len(data):,} of {len(full):,} accepted bookings. Click table headers to sort.')
    st.dataframe(data, hide_index=True, width='stretch')
    schema = pd.DataFrame({'column': data.columns, 'dtype': data.dtypes.astype(str).values,
                           'missing_values': data.isna().sum().values})
    st.subheader('Filtered schema & completeness')
    st.dataframe(schema, hide_index=True, width='stretch')
    st.write(f'Duplicate booking IDs in filtered accepted data: {int(data.booking_id.duplicated().sum())}')
    if not data.empty:
        st.subheader('Filtered numeric statistics')
        st.dataframe(data[['booking_value', 'cost', 'star_rating']].describe(), width='stretch')
    st.subheader('Original import quality report — entire dataset')
    quality_panel(*quality_report(DB, dataset_id))


def main():
    initialize(DB)
    available = datasets(DB)
    if available.empty:
        seed_demo()
        available = datasets(DB)
    with st.sidebar:
        st.title('🏨 StayScope')
        st.caption('BOOKING INTELLIGENCE')
        page = st.radio('Workspace', ['Overview', 'Cancellation explorer', 'Dataset explorer', 'Import & quality'])
        options = available.id.tolist()
        dataset_id = st.selectbox('Active dataset', options, format_func=lambda x: f"#{x} · {available.set_index('id').loc[x, 'name']}")
    if page == 'Import & quality':
        import_page()
        return
    metadata = available.set_index('id').loc[dataset_id]
    with st.spinner('Loading booking snapshot…'):
        full = load_dataset(DB, dataset_id)
    if full.empty:
        st.info('This dataset has no records. Import a reviewed file to begin.')
        return
    with st.sidebar:
        st.divider()
        st.subheader('Refine your view')
        date_range = st.date_input('Booking date', value=(full.booking_date.min().date(), full.booking_date.max().date()),
                                   key=f'dates_{dataset_id}')
        selections = {}
        for dim in ['city', 'property', 'channel', 'room_type', 'status']:
            values = sorted(full[dim].unique().tolist())
            selections[dim] = st.multiselect(dim.replace('_', ' ').title(), values, default=values,
                                              key=f'{dim}_{dataset_id}')
        rating_data = full.copy()
        rating_data['rating_label'] = full.star_rating.map(lambda x: 'Unknown' if pd.isna(x) else f'{int(x)} stars')
        values = sorted(rating_data.rating_label.unique().tolist())
        selections['rating_label'] = st.multiselect('Star rating', values, default=values, key=f'rating_{dataset_id}')
        st.caption('Clear a selection to match no records. Restore all options to remove that filter.')
    if len(date_range) != 2:
        st.info('Choose both a start and end booking date.')
        return
    filtered = filter_bookings(rating_data, *date_range, selections).drop(columns='rating_label')
    if metadata.is_demo:
        st.info(f'SYNTHETIC DEMONSTRATION DATA · {len(full):,} accepted bookings in this snapshot · Not real hotel results')
    else:
        st.caption(f"ACTIVE DATASET · {metadata['name']} · #{dataset_id}")
    if page == 'Overview':
        overview(filtered, metadata.currency)
    elif page == 'Cancellation explorer':
        comparisons(filtered)
    else:
        explorer(filtered, full, dataset_id)
    st.divider()
    st.subheader('Take this view with you')
    context = {'dataset_id': dataset_id, 'dataset_name': metadata['name'], 'synthetic': bool(metadata.is_demo),
               'currency': metadata.currency, 'date_range': date_range, 'filters': selections}
    cols = st.columns(3)
    cols[0].download_button('Filtered bookings · CSV', csv_bytes(filtered), 'filtered_bookings.csv', 'text/csv')
    cols[1].download_button('Summary & findings · CSV', csv_bytes(summary_frame(filtered, context)), 'summary.csv', 'text/csv')
    cols[2].download_button('Complete report · Excel', excel_bytes(filtered, context), 'booking_report.xlsx',
                            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    st.caption('StayScope · Business Intelligence & Booking Analytics Platform · Version 1')


try:
    main()
except DataError as exc:
    st.error(str(exc))
except (sqlite3.Error, OSError) as exc:
    st.error('Could not access the local database or sample file. Check folder permissions and retry. '
             'Close other processes holding the database if it is locked.')
    st.caption(f'Diagnostic: {type(exc).__name__}')
