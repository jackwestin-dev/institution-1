import pandas as pd
import streamlit as st
from datetime import datetime, date
import hmac
import altair as alt

st.set_page_config(page_title='Institutuion 1 Student Dashboard',layout='wide')

st.title('Institution 1 - Student Dashboard')

# Password protection
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the passward is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

## Read data from CSV files
df_engagement_attendance = pd.read_csv('./student-data/institution-1-engagement-data.csv',parse_dates=['start_date','end_date'])
df_test_scores = pd.read_csv('./student-data/institution-1-test-data.csv',parse_dates=['test_date'])

## Create dashboard filters
student_id = st.selectbox("Choose a student:", list(df_engagement_attendance['student_id'].unique()))

## Transform dataframes
df_engagement_attendance_student_filtered = df_engagement_attendance[df_engagement_attendance['student_id'] == student_id]
df_engagement_attendance_student_filtered['num_attended_large_session_cumsum'] = df_engagement_attendance_student_filtered['num_attended_large_session'].cumsum()
df_engagement_attendance_student_filtered['num_scheduled_large_session_cumsum'] = df_engagement_attendance_student_filtered['num_scheduled_large_session'].cumsum()
df_engagement_attendance_student_filtered['num_attended_small_session_cumsum'] = df_engagement_attendance_student_filtered['num_attended_small_session'].cumsum()
df_engagement_attendance_student_filtered['num_scheduled_small_session_cumsum'] = df_engagement_attendance_student_filtered['num_scheduled_small_session'].cumsum()
df_engagement_attendance_student_filtered['large_session'] = df_engagement_attendance_student_filtered['num_attended_large_session_cumsum'] / df_engagement_attendance_student_filtered['num_scheduled_large_session_cumsum']
df_engagement_attendance_student_filtered['small_session'] = df_engagement_attendance_student_filtered['num_attended_small_session_cumsum'] / df_engagement_attendance_student_filtered['num_scheduled_small_session_cumsum']
df_engagement_attendance_avg = df_engagement_attendance_student_filtered.mean()[['class_participation','homework_participation','cars_accuracy','sciences_accuracy','class_accuracy']]

class_participation = df_engagement_attendance_avg.loc['class_participation']
homework_participation = df_engagement_attendance_avg.loc['homework_participation']
cars_accuracy = df_engagement_attendance_avg.loc['cars_accuracy']
sciences_accuracy = df_engagement_attendance_avg.loc['sciences_accuracy']
class_accuracy = df_engagement_attendance_avg.loc['class_accuracy']

df_test_scores_student_filtered = df_test_scores[df_test_scores['student_id'] == student_id]

## Create sections and render dashboard
st.write(' ')
st.write(' ')
st.header('Participation')
st.write('The student has weekly average rates of {class_participation:.1%} for class participation and {homework_participation:.1%} for homework participation.'.format(class_participation=class_participation,homework_participation=homework_participation))
st.write(' ')
st.write(' ')

line_participation = alt.Chart(df_engagement_attendance_student_filtered).mark_line(point=True).transform_fold(
    fold=['class_participation', 'homework_participation'], 
    as_=['variable', 'value']
).encode(
    x=alt.X(
        'week:O',
        axis=alt.Axis(
            labelAngle=0,
            title='Week'
        )
    ),
    y=alt.Y(
        'value:Q',
        axis=alt.Axis(
            title='Participation Rate',
            format='%'
        )
    ),
    tooltip=[
        alt.Tooltip('week:O',title='Week'),
        alt.Tooltip('value:Q',title='Participation Rate',format='0.1%')
    ],
    color=alt.Color('variable:N',legend=alt.Legend(title='Setting',orient='bottom'))
)

st.altair_chart(line_participation,use_container_width=True)

st.write(' ')
st.write(' ')
st.header('Accuracy')
st.write('The student has weekly average scores of {cars_accuracy:.1%} for cars accuracy, {sciences_accuracy:.1%} for sciences accuracy, and {class_accuracy:.1%} for class accuracy.'.format(cars_accuracy=cars_accuracy,sciences_accuracy=sciences_accuracy,class_accuracy=class_accuracy))
st.write(' ')
st.write(' ')

line_engagement = alt.Chart(df_engagement_attendance_student_filtered).mark_line(point=True).transform_fold(
    fold=['sciences_accuracy', 'cars_accuracy','class_accuracy'], 
    as_=['variable', 'value']
).encode(
    x=alt.X(
        'week:O',
        axis=alt.Axis(
            labelAngle=0,
            title='Week'
        )
    ),
    y=alt.Y(
        'value:Q',
        axis=alt.Axis(
            title='Accuracy Score',
            format='%'
        )
    ),
    tooltip=[
        alt.Tooltip('week:O',title='Week'),
        alt.Tooltip('value:Q',title='Accuracy Rate',format='0.1%')
    ],
    color=alt.Color('variable:N',legend=alt.Legend(title='Subject',orient='bottom'))
)

st.altair_chart(line_engagement,use_container_width=True)

st.write(' ')
st.write(' ')
st.header('Attendance')
st.write(' ')
st.write(' ')

line_attendance = alt.Chart(df_engagement_attendance_student_filtered).mark_line(point=True).transform_fold(
    fold=['large_session','small_session'],
    as_=['variable','value']
).encode(
    x=alt.X(
        'week:O',
        axis=alt.Axis(
            labelAngle=0,
            title='Week'
        )
    ),
    y=alt.Y(
        'value:Q',
        axis=alt.Axis(
            title='Cumulative Attendance Rate',
            format='%'
        )
    ),
    tooltip=[
        alt.Tooltip('week:O',title='Week'),
        alt.Tooltip('value:Q',title='Cumulative Attendance Rate',format='0.1%')
    ],
    color=alt.Color('variable:N',legend=alt.Legend(title='Session Size',orient='bottom'))
)

st.altair_chart(line_attendance,use_container_width=True)

st.write(' ')
st.write(' ')
st.header('Practice Exams')
st.write(' ')
st.write(' ')

st.dataframe(df_test_scores_student_filtered[['test_name','test_date','actual_exam_score','low_predicted_exam_score','high_predicted_exam_score']],use_container_width=True)
st.write(' ')
st.write(' ')

point_exam_scores = alt.Chart(df_test_scores_student_filtered).mark_point().transform_fold(
    fold=['actual_exam_score','low_predicted_exam_score','high_predicted_exam_score'],
    as_=['variable','value']
).encode(
    x=alt.X(
        'yearmonthdate(test_date):O',
        axis=alt.Axis(
            labelAngle=-45,
            title='Test Date'
        )
    ),
    y=alt.Y(
        'value:Q',
        axis=alt.Axis(
            title='Exam Score'
        ),
        scale=alt.Scale(domain=[470, 528])
    ),
    color=alt.Color('variable:N',legend=alt.Legend(title='Range',orient='bottom'))
)

st.altair_chart(point_exam_scores,use_container_width=True)