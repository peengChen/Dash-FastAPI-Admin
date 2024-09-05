import dash
from dash import dcc
import feffery_utils_components as fuc
from dash.dependencies import Input, Output, State
from flask import session
from server import app
from api.config import query_config_list_api


# api拦截器——退出登录二次确认
@app.callback(
    [Output('redirect-container', 'children', allow_duplicate=True),
     Output('token-container', 'data', allow_duplicate=True)],
    Input('token-invalid-modal', 'okCounts'),
    prevent_initial_call=True
)
def redirect_page(okCounts):

    if okCounts:
        session.clear()

        return [
            dcc.Location(
                pathname='/login',
                id='index-redirect'
            ),
            None
        ]

    return [dash.no_update] * 2


# 应用初始化主题颜色
@app.callback(
    Output('system-app-primary-color-container', 'data'),
    Input('app-mount', 'id'),
    State('custom-app-primary-color-container', 'data')
)
def get_primary_color(_, custom_color):
    # if not custom_color:
    #     primary_color_res = query_config_list_api(config_key='sys.index.skinName')
    #     if primary_color_res.get('code') == 200:
    #         primary_color = primary_color_res.get('data')

    #         return primary_color

    return dash.no_update


app.clientside_callback(
    '''
    (system_color, custom_color) => {
        if (custom_color) {
            return custom_color;
        }
        return system_color;
    }
    ''',
    Output('app-config-provider', 'primaryColor'),
    [Input('system-app-primary-color-container', 'data'),
     Input('custom-app-primary-color-container', 'data')],
    prevent_initial_call=True
)
