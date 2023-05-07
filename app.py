import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

paragraph1 = '''
The article explores the gender wage gap in the United States and Puerto Rico based on the 2019 American Community Survey (ACS) and 2019 Puerto Rico Community Survey data1.
The article provides a data visualization tool that shows the median earnings by sex, the top occupation by sex, and the wage gap by sex for each state’s top occupation1.
The article reports that the national median earnings for civilians who worked full-time, year-round in the past 12 months was 53,544 for men compared to \\$43,394 for women, a difference of \$10,1501.
The article also highlights some of the factors that may contribute to earnings differences between women and men, such as age, hours worked, presence of children, education, and occupation type1.
The article notes that the wage gap varies by state, with Wyoming having the largest gap of \$21,676 and Puerto Rico having no statistically significant gap1.
The article mentions that Equal Pay Day, which marks how far into the year women must work to equal what men earned the previous year, is on March 15 this year, earlier than ever since its inception in 19961. The article is presented here https://www.census.gov/library/stories/2022/03/what-is-the-gender-wage-gap-in-your-state.html
'''

paragraph2 = '''
The GSS is a nationally representative survey of adults in the United States conducted since 1972. It collects data on contemporary American society in order to monitor and explain trends in opinions, attitudes and behaviors. The GSS contains a standard core of demographic, behavioral, and attitudinal questions, plus topics of special interest. Among the topics covered are civil liberties, crime and violence, intergroup tolerance, morality, national spending priorities, psychological well-being, social mobility, and stress and traumatic events. The GSS aims to make high-quality data easily accessible to scholars, students, policy-makers, and others with minimal cost and waiting. The article is located at https://gss.norc.org/about-the-gss.
'''

modDf = gss_clean.groupby('sex')[['income', 'job_prestige', 'socioeconomic_index', 'education']].mean()
modDf = pd.DataFrame(modDf.reset_index())

modDf = modDf.rename(columns={
    'sex': 'Gender',
    'income': 'Annual Income (in USD)',
    'job_prestige': 'Job Prestige Score',
    'socioeconomic_index': 'Socioeconomic Index',
    'education': 'Years of Education'
})
modDf = round(modDf,2)
modDf

table = ff.create_table(modDf)
table.show()

modDf = gss_clean.groupby(['male_breadwinner', 'sex'])[['sex']].size()
modDf = pd.DataFrame(modDf.reset_index())
modDf = modDf.rename(columns = {'sex':'Sex',0:'Count'})
modDf


fig3 = px.bar(modDf, x = 'Sex', y = 'Count', color = 'male_breadwinner',  barmode = 'group')
fig3.show()

fig4 = px.scatter(gss_clean, x='job_prestige', y='income', color = 'sex', trendline='ols',
                 height=600, width=600,
                 hover_data=['education', 'socioeconomic_index'])
fig4.show()

fig5 = px.box(gss_clean, x='sex', y = 'income',
labels={'sex':'Sex of Respondant', 'income':'Income Earned per Year'})
fig5.show()

fig5cont = px.box(gss_clean, x='sex', y = 'job_prestige',
            labels={'sex':'Sex of Respondant', 'job_prestige':'Prestige of Job'}
            )
fig5cont.show()

new_df = gss_clean[['income', 'sex', 'job_prestige']]

# Create a new feature with six equally sized categories
new_df['job_prestige_category'] = pd.qcut(new_df['job_prestige'], q=6, labels=False)

# Drop rows with missing values
new_df = new_df.dropna()

new_df

fig6 = px.box(new_df, x = 'sex', y = 'income', facet_col = 'job_prestige_category', facet_col_wrap=2)
fig6.show()

app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.H1("Exploring the Gender Wage Gap using the GSS Data Set"),  
        dcc.Markdown(children = paragraph1),
        dcc.Markdown(children = paragraph2),

        html.H2("Comparing Statistics Based on Sex"),
        dcc.Graph(figure=table),
        
        html.H2("Opinions on Male Being the Breadwinner"),
        dcc.Graph(figure=fig3),
        
        html.H2("Job Prestige vs. Income for both Sexes"),
        dcc.Graph(figure=fig4),
        
        html.Div([
            
        html.H2("Distribution of Sex and Income"),
        
        dcc.Graph(figure=fig5)
            
        ], style = {'width':'48%', 'float':'left'}),
        
        html.Div([
            
        html.H2("Distribution of Sex and Prestige"),
        
        dcc.Graph(figure=fig5cont)
            
        ], style = {'width':'48%', 'float':'right'}),

        
        html.H2("Distribution of Sex and Income Seperated by Prestige"),
        
        dcc.Graph(figure=fig6)
    ]
)


if __name__ == '__main__':
    app.run_server(debug=True)
