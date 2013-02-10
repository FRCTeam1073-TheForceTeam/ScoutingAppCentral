'''
Created on Feb 08, 2013

@author: ksthilaire
'''


def gen_js_store_files(attr_definitions):
    js_store_fragment_start = "Ext.define('MyApp.store.MyJsonStore', {\n" + \
                              "    extend: 'Ext.data.Store',\n" +\
                              "\n" +\
                              "    constructor: function(cfg) {\n" +\
                              "        var me = this;\n" +\
                              "        cfg = cfg || {};\n" +\
                              "        me.callParent([Ext.apply({\n" + \
                              "            autoLoad: true,\n" + \
                              "            storeId: 'MyJsonStore',\n" + \
                              "            proxy: {\n" + \
                              "                type: 'ajax',\n" + \
                              "                url: '/test',\n" + \
                              "                reader: {\n" + \
                              "                    type: 'json',\n" + \
                              "                    root: 'attributes'\n" + \
                              "                }\n" + \
                              "            },\n" + \
                              "            fields: [\n" + \
                              "                {\n" + \
                              "                    name: 'Team'\n" + \
                              "                },\n" + \
                              "                {\n" + \
                              "                    name: 'Score'\n" + \
                              "                }"

    js_store_fragment_end = "            ]\n" + \
                            "        }, cfg)]);\n" + \
                            "    }\n" + \
                            "});\n"

    js_panel_fragment_start="Ext.define('MyApp.view.ui.MyTabPanel1', {\n" + \
                            "    extend: 'Ext.panel.Panel',\n" + \
                            "\n" + \
                            "    height: 700,\n" + \
                            "    width: 1200,\n" + \
                            "\n" + \
                            "    initComponent: function() {\n" + \
                            "        var me = this;\n" + \
                            "\n" + \
                            "        Ext.applyIf(me, {\n" + \
                            "            items: [\n" + \
                            "                {\n" + \
                            "                    xtype: 'panel',\n" + \
                            "                    title: 'Scouting Application',\n" + \
                            "                    items: [\n" + \
                            "                        {\n" + \
                            "                            xtype: 'gridpanel',\n" + \
                            "                            height: 666,\n" + \
                            "                            width: 1200,\n" + \
                            "                            autoScroll: true,\n" + \
                            "                            title: 'Team Attributes',\n" + \
                            "                            store: 'MyJsonStore',\n" + \
                            "                            features: [\n" + \
                            "                                {\n" + \
                            "                                    ftype: 'grouping'\n" + \
                            "                                }\n" + \
                            "                            ],\n" + \
                            "                            columns: [\n" + \
                            "                                {\n" + \
                            "                                    dataIndex: 'Team',\n" + \
                            "                                    text: 'Team'\n" + \
                            "                                },\n" + \
                            "                                {\n" + \
                            "                                    dataIndex: 'Score',\n" + \
                            "                                    text: 'Score'\n" + \
                            "                                }"



    js_panel_fragment_end = "                            ],\n" + \
                            "                            viewConfig: {\n" + \
                            "\n" + \
                            "                            }\n" + \
                            "                        }\n" + \
                            "                    ]\n" + \
                            "                },\n" + \
                            "                {\n" + \
                            "                    xtype: 'panel',\n" + \
                            "                    title: 'Tab 2'\n" + \
                            "                },\n" + \
                            "                {\n" + \
                            "                    xtype: 'panel',\n" + \
                            "                    title: 'Tab 3'\n" + \
                            "                }\n" + \
                            "            ]\n" + \
                            "        });\n" + \
                            "\n" + \
                            "        me.callParent(arguments);\n" + \
                            "    }\n" + \
                            "});\n"
    
    attr_dict = attr_definitions.get_definitions()
    attr_order = [{} for i in range(len(attr_dict))]
    for key, value in attr_dict.items():
        offset = value['Column_Order']
        offset1 = float(offset)
        offset2 = int(offset1)
        
        attr_order[(int(float(value['Column_Order']))-1)] = value

    js_store_string = js_store_fragment_start
    js_panel_string = js_panel_fragment_start
    for attr_def in attr_order:
        if ( attr_def['Include_In_Report'] == 'Yes'):
            js_store_string += ",\n                {\n"
            js_store_string += "                    name: '" + attr_def['Name'] + "'\n"
            js_store_string += "                }"

            js_panel_string += ",\n                                {\n"
            js_panel_string += "                                    dataIndex: '" + attr_def['Name'] + "',\n"
            js_panel_string += "                                    text: '" + attr_def['Name'] + "'\n"
            js_panel_string += "                                }"
                        
            
    js_store_string += "\n"
    js_store_string += js_store_fragment_end
    js_panel_string += "\n"
    js_panel_string += js_panel_fragment_end
    
    outputFilename = './static/test/app/store/MyJsonStore.js'
    fo = open(outputFilename, "w+")
    fo.write( js_store_string )
    fo.close()

    outputFilename = './static/test/app/view/ui/MyTabPanel1.js'
    fo = open(outputFilename, "w+")
    fo.write( js_panel_string )
    fo.close()
