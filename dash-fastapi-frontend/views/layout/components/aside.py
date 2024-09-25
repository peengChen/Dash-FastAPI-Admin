import dash
from dash import dcc
import feffery_antd_components as fac
from callbacks.layout_c import aside_c  # noqa: F401


def render_aside_content(menu_info):
    return [
        dcc.Store(id='current-key_path-store'),
        dcc.Store(id='current-item-store'),
        dcc.Store(id='current-item_path-store'),
        fac.AntdSider(
            [
                fac.AntdRow(
                    [
                        fac.AntdCol(
                            fac.AntdImage(
                                width=32,
                                height=32,
                                src=dash.get_asset_url('imgs/logo.png'),
                                preview=False,
                            ),
                            flex='1',
                            style={
                                'height': '100%',
                                'display': 'flex',
                                'alignItems': 'center',
                            },
                        ),
                        fac.AntdCol(
                            fac.AntdText(
                                '后台管理系统',
                                id='logo-text',
                                style={
                                    'fontSize': '22px',
                                    # 'paddingLeft': '20px',
                                    'color': 'rgb(255, 255, 255)',
                                },
                            ),
                            flex='5',
                            style={
                                'height': '100%',
                                'display': 'flex',
                                'alignItems': 'center',
                            },
                        ),
                    ],
                    style={
                        'height': '50px',
                        'background': '#001529',
                        'position': 'sticky',
                        'top': 0,
                        'zIndex': 999,
                        'paddingLeft': '10px',
                    },
                ),
                fac.AntdMenu(
                    id='index-side-menu',
                    menuItems=menu_info,
                    mode='inline',
                    theme='dark',
                    defaultSelectedKey='首页',
                    style={'width': '100%', 'height': 'calc(100vh - 50px)'},
                ),
            ],
            id='menu-collapse-sider-custom',
            collapsible=True,
            collapsedWidth=60,
            trigger=None,
            width=210,
        ),
    ]
