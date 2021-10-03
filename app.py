import numpy as np
import pandas as pd

import bokeh.io
import bokeh.plotting
import bokeh.models
import bokeh.palettes

from bokeh.transform import dodge

import panel as pn

pn.extension()



df = pd.read_csv('NiVCases.csv')

def bar_graphs(df):
    
    p = bokeh.plotting.figure(width=1000, height=500,
                              x_range=np.sort(list(df.Country.unique())),
                              x_axis_label='Country',
                              y_axis_label='Number of People',
                              title="Total Nipah Virus Cases by Country",
                              tooltips=[("Cases", "@Cases"), ("Deaths", "@Deaths")])
    
    df_slice = df.groupby(['Country'])['Country', 'Cases', 'Deaths'].sum().reset_index().sort_values(by="Country")
    
    source = bokeh.models.ColumnDataSource(df_slice)
    
    p.vbar(x=dodge("Country", -0.1, range=p.x_range), top="Cases", width=0.2, color="#1f77b4", legend_label="Cases", source=source)
    p.vbar(x=dodge("Country", 0.105, range=p.x_range), top="Deaths", width=0.2, color="darkorange", legend_label="Deaths", source=source)
    
    p.title.text_font_size = "13pt"
    p.title.align = 'center'
    p.xgrid.grid_line_color = None
    p.axis.axis_label_text_font_size = "11pt"
    p.axis.major_label_text_font_size = "10pt"
    
    return pn.Row(pn.layout.HSpacer(), p, pn.layout.HSpacer())



country_select = pn.widgets.RadioBoxGroup(options=['Bangladesh', 'India'], value='Bangladesh')
country_box = pn.WidgetBox('<h3><b>Select Country</b></h3>', country_select)

data_select = pn.widgets.CheckBoxGroup(options=['Cases', 'Deaths'], value=['Cases', 'Deaths'])
data_box = pn.WidgetBox('<h3><b>Select Data to Plot</b></h3>', data_select)


@pn.depends(country_select.param.value,
            data_select.param.value)
def cases_plot(country='Bangladesh', 
               data_lst=['Cases', 'Deaths']):
        
    if country not in df.Country.values:
        raise ValueError("Provided country name is invalid!")
        
    # group by year and country first
    df_slice = df.groupby(['Year', 'Country'])['Country', 'Cases', 'Deaths'].sum().reset_index()
    
    df_slice = df_slice[df_slice['Country'] == country]
        
    p = bokeh.plotting.figure(height=500,
                              width=1000,
                              title=f"Nipah Virus Cases and Deaths in {country}",
                              x_axis_label='Year',
                              y_axis_label='Number of People')
    
    source = bokeh.models.ColumnDataSource(df_slice)
    
    hover_renderers = []
    hover_tooltips = []
    
    if 'Cases' in data_lst:
        circle_1 = bokeh.models.Circle(x="Year", y="Cases", fill_color="#1f77b4", line_color="#1f77b4", size=8)
        line_1 = bokeh.models.Line(x="Year", y="Cases", line_color="#1f77b4")
        
        circle_renderer_1 = p.add_glyph(source, circle_1)
        
        hover_renderers.append(circle_renderer_1)
        hover_tooltips.append(("Cases", "@Cases"))
        
        p.add_glyph(source, line_1)
        
    if 'Deaths' in data_lst:
        circle_2 = bokeh.models.Circle(x="Year", y="Deaths", fill_color="darkorange", line_color="darkorange", size=8)
        line_2 = bokeh.models.Line(x="Year", y="Deaths", line_color="darkorange")
        
        circle_renderer_2 = p.add_glyph(source, circle_2)
        hover_renderers.append(circle_renderer_2)
        hover_tooltips.append(("Deaths", "@Deaths"))
        
        p.add_glyph(source, glyph=line_2)
    
    points_hover = bokeh.models.HoverTool(renderers=hover_renderers, tooltips=hover_tooltips)
    p.add_tools(points_hover)
    p.xaxis.ticker = bokeh.models.FixedTicker(ticks=np.arange(df_slice.Year.min(), df_slice.Year.max() + 1))
        
    p.title.text_font_size = "13pt"
    p.title.align = 'center'
    p.xgrid.grid_line_color = None
    p.axis.axis_label_text_font_size = "11pt"
    p.axis.major_label_text_font_size = "10pt"
        
    return p


plot_tab = pn.Row(pn.layout.HSpacer(),
                  cases_plot, 
                  pn.Spacer(width=10),
                  pn.Column(pn.layout.VSpacer(),
                             data_box,
                             pn.Spacer(height=10),
                             country_box,
                             pn.layout.VSpacer()
                            ),
                  pn.layout.HSpacer(),
                  )


dashboard = pn.Tabs(("Bar Graph", bar_graphs(df)), ("Cases Count", plot_tab))


# make it servable
dashboard.servable()
