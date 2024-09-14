import feffery_antd_components as fac
from dash import dcc, html
from api.system.dept import DeptApi
from callbacks.system_c import dept_c  # noqa: F401
from utils.permission_util import PermissionManager
from utils.tree_tool import list_to_tree


def render(*args, **kwargs):
    default_expanded_row_keys = []
    table_info = DeptApi.list_dept({})
    table_data = table_info['data']
    for item in table_data:
        default_expanded_row_keys.append(str(item['dept_id']))
        item['key'] = str(item['dept_id'])
        if item['parent_id'] == 0:
            item['operation'] = [
                {'content': '修改', 'type': 'link', 'icon': 'antd-edit'}
                if PermissionManager.check_perms('system:dept:edit')
                else {},
                {'content': '新增', 'type': 'link', 'icon': 'antd-plus'}
                if PermissionManager.check_perms('system:dept:add')
                else {},
            ]
        elif item['status'] == '1':
            item['operation'] = [
                {'content': '修改', 'type': 'link', 'icon': 'antd-edit'}
                if PermissionManager.check_perms('system:dept:edit')
                else {},
                {'content': '删除', 'type': 'link', 'icon': 'antd-delete'}
                if PermissionManager.check_perms('system:dept:remove')
                else {},
            ]
        else:
            item['operation'] = [
                {'content': '修改', 'type': 'link', 'icon': 'antd-edit'}
                if PermissionManager.check_perms('system:dept:edit')
                else {},
                {'content': '新增', 'type': 'link', 'icon': 'antd-plus'}
                if PermissionManager.check_perms('system:dept:add')
                else {},
                {'content': '删除', 'type': 'link', 'icon': 'antd-delete'}
                if PermissionManager.check_perms('system:dept:remove')
                else {},
            ]
        if item['status'] == '0':
            item['status'] = dict(tag='正常', color='blue')
        else:
            item['status'] = dict(tag='停用', color='volcano')
    table_data_new = list_to_tree(table_data, 'dept_id', 'parent_id')

    return [
        # 部门管理模块操作类型存储容器
        dcc.Store(id='dept-operations-store'),
        # 部门管理模块弹窗类型存储容器
        dcc.Store(id='dept-modal_type-store'),
        # 部门管理模块表单数据存储容器
        dcc.Store(id='dept-form-store'),
        # 部门管理模块删除操作行key存储容器
        dcc.Store(id='dept-delete-ids-store'),
        fac.AntdRow(
            [
                fac.AntdCol(
                    [
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    html.Div(
                                        [
                                            fac.AntdForm(
                                                [
                                                    fac.AntdSpace(
                                                        [
                                                            fac.AntdFormItem(
                                                                fac.AntdInput(
                                                                    id='dept-dept_name-input',
                                                                    placeholder='请输入部门名称',
                                                                    autoComplete='off',
                                                                    allowClear=True,
                                                                    style={
                                                                        'width': 240
                                                                    },
                                                                ),
                                                                label='部门名称',
                                                            ),
                                                            fac.AntdFormItem(
                                                                fac.AntdSelect(
                                                                    id='dept-status-select',
                                                                    placeholder='部门状态',
                                                                    options=[
                                                                        {
                                                                            'label': '正常',
                                                                            'value': '0',
                                                                        },
                                                                        {
                                                                            'label': '停用',
                                                                            'value': '1',
                                                                        },
                                                                    ],
                                                                    style={
                                                                        'width': 240
                                                                    },
                                                                ),
                                                                label='部门状态',
                                                            ),
                                                            fac.AntdFormItem(
                                                                fac.AntdButton(
                                                                    '搜索',
                                                                    id='dept-search',
                                                                    type='primary',
                                                                    icon=fac.AntdIcon(
                                                                        icon='antd-search'
                                                                    ),
                                                                )
                                                            ),
                                                            fac.AntdFormItem(
                                                                fac.AntdButton(
                                                                    '重置',
                                                                    id='dept-reset',
                                                                    icon=fac.AntdIcon(
                                                                        icon='antd-sync'
                                                                    ),
                                                                )
                                                            ),
                                                        ],
                                                        style={
                                                            'paddingBottom': '10px'
                                                        },
                                                    ),
                                                ],
                                                layout='inline',
                                            )
                                        ],
                                        hidden=False,
                                        id='dept-search-form-container',
                                    ),
                                )
                            ]
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdSpace(
                                        [
                                            fac.AntdButton(
                                                [
                                                    fac.AntdIcon(
                                                        icon='antd-plus'
                                                    ),
                                                    '新增',
                                                ],
                                                id={
                                                    'type': 'dept-operation-button',
                                                    'index': 'add',
                                                },
                                                style={
                                                    'color': '#1890ff',
                                                    'background': '#e8f4ff',
                                                    'border-color': '#a3d3ff',
                                                },
                                            )
                                            if PermissionManager.check_perms(
                                                'system:dept:add'
                                            )
                                            else [],
                                            fac.AntdButton(
                                                [
                                                    fac.AntdIcon(
                                                        icon='antd-swap'
                                                    ),
                                                    '展开/折叠',
                                                ],
                                                id='dept-fold',
                                                style={
                                                    'color': '#909399',
                                                    'background': '#f4f4f5',
                                                    'border-color': '#d3d4d6',
                                                },
                                            ),
                                        ],
                                        style={'paddingBottom': '10px'},
                                    ),
                                    span=16,
                                ),
                                fac.AntdCol(
                                    fac.AntdSpace(
                                        [
                                            html.Div(
                                                fac.AntdTooltip(
                                                    fac.AntdButton(
                                                        [
                                                            fac.AntdIcon(
                                                                icon='antd-search'
                                                            ),
                                                        ],
                                                        id='dept-hidden',
                                                        shape='circle',
                                                    ),
                                                    id='dept-hidden-tooltip',
                                                    title='隐藏搜索',
                                                )
                                            ),
                                            html.Div(
                                                fac.AntdTooltip(
                                                    fac.AntdButton(
                                                        [
                                                            fac.AntdIcon(
                                                                icon='antd-sync'
                                                            ),
                                                        ],
                                                        id='dept-refresh',
                                                        shape='circle',
                                                    ),
                                                    title='刷新',
                                                )
                                            ),
                                        ],
                                        style={
                                            'float': 'right',
                                            'paddingBottom': '10px',
                                        },
                                    ),
                                    span=8,
                                    style={'paddingRight': '10px'},
                                ),
                            ],
                            gutter=5,
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdSpin(
                                        fac.AntdTable(
                                            id='dept-list-table',
                                            data=table_data_new,
                                            columns=[
                                                {
                                                    'dataIndex': 'dept_id',
                                                    'title': '部门编号',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                    'hidden': True,
                                                },
                                                {
                                                    'dataIndex': 'dept_name',
                                                    'title': '部门名称',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'order_num',
                                                    'title': '排序',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'status',
                                                    'title': '状态',
                                                    'renderOptions': {
                                                        'renderType': 'tags'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'create_time',
                                                    'title': '创建时间',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'title': '操作',
                                                    'dataIndex': 'operation',
                                                    'renderOptions': {
                                                        'renderType': 'button'
                                                    },
                                                },
                                            ],
                                            bordered=True,
                                            pagination={
                                                'hideOnSinglePage': True
                                            },
                                            defaultExpandedRowKeys=default_expanded_row_keys,
                                            style={
                                                'width': '100%',
                                                'padding-right': '10px',
                                                'padding-bottom': '20px',
                                            },
                                        ),
                                        text='数据加载中',
                                    ),
                                )
                            ]
                        ),
                    ],
                    span=24,
                )
            ],
            gutter=5,
        ),
        # 新增和编辑部门表单modal
        fac.AntdModal(
            [
                fac.AntdForm(
                    [
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    html.Div(
                                        [
                                            fac.AntdFormItem(
                                                fac.AntdTreeSelect(
                                                    id='dept-tree-select',
                                                    name='parent_id',
                                                    placeholder='请选择上级部门',
                                                    treeData=[],
                                                    treeNodeFilterProp='title',
                                                    style={'width': '100%'},
                                                ),
                                                label='上级部门',
                                                required=True,
                                                id={
                                                    'type': 'dept-form-label',
                                                    'index': 'parent_id',
                                                    'required': True,
                                                },
                                                labelCol={'span': 4},
                                                wrapperCol={'span': 20},
                                            ),
                                        ],
                                        id='dept-parent_id-div',
                                        hidden=False,
                                    ),
                                    span=24,
                                ),
                            ]
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdInput(
                                            name='dept_name',
                                            placeholder='请输入部门名称',
                                            allowClear=True,
                                            style={'width': '100%'},
                                        ),
                                        label='部门名称',
                                        required=True,
                                        id={
                                            'type': 'dept-form-label',
                                            'index': 'dept_name',
                                            'required': True,
                                        },
                                    ),
                                    span=12,
                                ),
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdInputNumber(
                                            name='order_num',
                                            min=0,
                                            style={'width': '100%'},
                                        ),
                                        label='显示顺序',
                                        required=True,
                                        id={
                                            'type': 'dept-form-label',
                                            'index': 'order_num',
                                            'required': True,
                                        },
                                    ),
                                    span=12,
                                ),
                            ],
                            gutter=5,
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdInput(
                                            name='leader',
                                            placeholder='请输入负责人',
                                            allowClear=True,
                                            style={'width': '100%'},
                                        ),
                                        label='负责人',
                                        id={
                                            'type': 'dept-form-label',
                                            'index': 'leader',
                                            'required': False,
                                        },
                                    ),
                                    span=12,
                                ),
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdInput(
                                            name='phone',
                                            placeholder='请输入联系电话',
                                            allowClear=True,
                                            style={'width': '100%'},
                                        ),
                                        label='联系电话',
                                        id={
                                            'type': 'dept-form-label',
                                            'index': 'phone',
                                            'required': False,
                                        },
                                    ),
                                    span=12,
                                ),
                            ],
                            gutter=5,
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdInput(
                                            name='email',
                                            placeholder='请输入邮箱',
                                            allowClear=True,
                                            style={'width': '100%'},
                                        ),
                                        label='邮箱',
                                        id={
                                            'type': 'dept-form-label',
                                            'index': 'email',
                                            'required': False,
                                        },
                                    ),
                                    span=12,
                                ),
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdRadioGroup(
                                            name='status',
                                            options=[
                                                {'label': '正常', 'value': '0'},
                                                {'label': '停用', 'value': '1'},
                                            ],
                                            defaultValue='0',
                                            style={'width': '100%'},
                                        ),
                                        label='部门状态',
                                        id={
                                            'type': 'dept-form-label',
                                            'index': 'status',
                                            'required': False,
                                        },
                                    ),
                                    span=12,
                                ),
                            ],
                            gutter=5,
                        ),
                    ],
                    id='dept-form',
                    enableBatchControl=True,
                    labelCol={'span': 8},
                    wrapperCol={'span': 16},
                    style={'marginRight': '15px'},
                )
            ],
            id='dept-modal',
            mask=False,
            width=650,
            renderFooter=True,
            okClickClose=False,
        ),
        # 删除部门二次确认modal
        fac.AntdModal(
            fac.AntdText('是否确认删除？', id='dept-delete-text'),
            id='dept-delete-confirm-modal',
            visible=False,
            title='提示',
            renderFooter=True,
            centered=True,
        ),
    ]
