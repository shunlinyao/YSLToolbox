'use strict';
function downloader_web_block() {
    this.selected_type = '';
    this.target_url = '';
    this.target_path = '';
    this.current_selected_type = '';
    this.current_selected_folder_tag = '';
    this.file_tag_relation = {};
    this.tag_list = [];
    this.selected_file = '';
    this.my_socket = null;
}

downloader_web_block.prototype.init = function () {
    var that = this;
    that.init_layout();
    that.init_listener();
    that.init_web_socket();
}

downloader_web_block.prototype.init_layout = function () {
    let that = this;
    let body_content = `
    <div style="display:flex; height:100%; width:100%; justify-content:center; align-items:center;">
        <div style="height:55rem; width:90rem; border: 2px solid #777; display:flex;padding:0.3rem;border-radius:0.4rem; ">
            <div style="height:100%; width:30%; display:flex; flex-direction:column; padding:0.2rem;">
                <div style="width:97%; border: 2px solid #00c80b;border-radius:0.4rem; padding:0.2rem;display:inline-block;">
                    <input id="target_path_id" type="text" class="dld_input" placeholder="LOCAL PATH" style="width:97%;">
                    <button id="ls_confirm" class="dld_btn" style="margin-top:0.2rem;width:100%;">确定资源根目录</button>
                    <div style="width:100%;height:1.8rem;display:inline-flex;margin-top:0.2rem;">
                        <button class="dld_type_btn" value="video" style="width:25%;border-radius-top-left:">视频</button>
                        <button class="dld_type_btn" value="image" style="width:25%;">图片</button>
                        <button class="dld_type_btn" value="cg" style="width:25%;">图文</button>
                        <button class="dld_type_btn" value="scene" style="width:25%;margin:0px;">场景</button>
                    </div>
                    <div id="file_tag_container" style="width:98%; max-height:4rem; display:block;overflow-y:auto;border: 1px solid #ccc;margin-top:0.2rem;padding:0.2rem;padding-bottom:0rem;">
                    </div>                    
                </div>
                
                <div style="width:97%; border: 2px solid #ffec00;border-radius:0.4rem; padding:0.2rem;display:inline-block;margin-top:0.8rem;">
                    <input id="ls_tag_name" type="text" class="dld_input" placeholder="新标签" style="width:97%;">
                    <button id="ls_tag_add" class="dld_btn" style="margin-top:0.2rem;width:100%;">添加标签</button>
                </div>
                
                <div style="width:97%; border: 1px solid #aaa;border-radius:0.4rem; padding:0.2rem;display:inline-block;margin-top:0.8rem;">
                    <input id="target_url_add" type="text" class="dld_input" placeholder="URL" style="width:97%;">
                    <button id="ls_test_connection" class="dld_btn" style="margin-top:0.2rem;width:100%;">测试对象服务链接</button>
                </div>
                
                <div style="width:98%;height:50%;margin-top:1rem;">            
                    <div class="dld_base_div" style="height:45%;">
                        <textarea id="json_area" style="height:100%; width:100%;resize:none;border:none;background-color:#fff;" disabled></textarea>
                    </div>
                    <div style="height:50%; width:98%; margin-top:2%; border: 1px solid #333;background-color:#222; border-radius:0.2rem;padding:0.3rem;">
                        <textarea id="terminal_area" style="color:#fff;height:100%; width:100%;resize:none;border:none;background-color:#222;"disabled></textarea>
                    </div>
                </div>
                <button id="ls_start_upload" class="dld_btn" style="margin-top:1rem;border:2px solid #333;">开始上传</button>
            </div>
            
            <div style="height:100%; width:70%; display:flex; flex-direction:column;padding:0.2rem;">
                <div id="type_tag_container" class="dld_base_div" style="height:20%; display:block;overflow-y:auto;border: 2px solid #ffec00;">
                </div>
                <div class="dld_base_div" style="height:70%; margin-top:0.8rem;overflow-y:auto;border: 2px solid #00c80b;">
                    <div id="type_file_container" class="file_grid_div" style="width:100%;">
                    </div>
                </div>
            </div>
        </div>
    </div>
    `;
    $('#downloader_container').html(body_content);
}

downloader_web_block.prototype.init_listener = function () {
    let that = this;
    $('#ls_test_connection').click(function () {
        that.test_connection();
    });
    $('#ls_confirm').click(function () {
        that.test_path('local_path_check');
    });
    $('#ls_start_upload').click(function () {
        if (confirm('确定开始上传？') == true) {
            that.test_path('start_upload');
        }
    });
    $('.dld_type_btn').click(function () {
        $('.dld_type_btn').css('background-color', '#fdfdfd');
        $(this).css('background-color', '#ebebeb');
        let rs_type = $(this).val();
        that.current_selected_type = rs_type;
        that.slect_type_path(rs_type);
        
    });
    $('#ls_tag_add').click(function () {
        that.tag_handler_action('add_tag');
    });
}

downloader_web_block.prototype.test_connection = function () {
    let that = this;
    that.target_url = $('#target_url_add').val();
    if (that.target_url == '') {
        alert('url不能为空');
        return;
    }
    let request_content = { 'url': that.target_url, 'header': {'Content-Type' : 'application/json'}, 'body':{} };
    that.resource_action('test_connection', request_content);
}

downloader_web_block.prototype.tag_handler_action = function (cmd) {
    let that = this;
    let tag_name = $('#ls_tag_name').val();
    if (tag_name == '') {
        alert('标签名不能为空');
        return;
    }
    if (that.current_selected_type == '') {
        alert('请先选择资源类型');
        return;
    }
    that.tag_list.push(tag_name);
    let tag_container = $('#type_tag_container');
    
    let request_content = { 'tag_name': tag_name, 'resource_type': that.current_selected_type};
    that.resource_action(cmd, request_content);
    let tag_button = $(`<button class="grid_tag_button" value="${tag_name}">` + tag_name + `</button>`);
    // tag_button onlick
    tag_button.click(function () {
        let selected_tag = $(this).val();
        if (that.selected_file == '') {
            alert('请先选择文件');
            return;
        }
        if (!(that.selected_file in that.file_tag_relation)){
            that.file_tag_relation[that.selected_file] = []
        }
        if (that.file_tag_relation[that.selected_file].includes(selected_tag)) {
            let index = that.file_tag_relation[that.selected_file].indexOf(selected_tag);
            that.file_tag_relation[that.selected_file].splice(index, 1);
            $(this).css('background-color', '#fafafa');
        }
        else {
            that.file_tag_relation[that.selected_file].push(selected_tag);
            $(this).css('background-color', '#ebebeb');
        }
        that.bind_file_tag();
    });
    tag_container.append(tag_button);
}

downloader_web_block.prototype.test_path = function (cmd) {
    let that = this;
    that.target_path = $('#target_path_id').val();
    if (that.target_path == '') {
        alert('路径不能为空');
        return;
    }
    let request_content = { 'path': that.target_path};
    that.resource_action(cmd, request_content);
}

downloader_web_block.prototype.slect_type_path = function (type) {
    let that = this;
    if (that.target_path == '') {
        alert('路径不能为空');
        return;
    }
    let request_content = { 'path': that.target_path + '/' + type, 'rs_type': type};
    that.resource_action('local_path_tree', request_content);
}

downloader_web_block.prototype.select_type_folder_tag = function (folder_tag) {
    let that = this;
    if (that.target_path == '') {
        alert('路径不能为空');
        return;
    }
    let type = that.current_selected_type;
    let request_content = { 'path': that.target_path + '/' + type + folder_tag, 'rs_type': type, 'folder_tag':folder_tag};
    that.resource_action('local_path_tag_tree', request_content);
}


downloader_web_block.prototype.resource_action = function (cmd, content) {
    let that = this;
    let param = { 'type': cmd, 'content': content };
    that.user_terminal_input(cmd, content);
    that.vm_ajax_util.load_json_post_fetch("/toolbox/tool_downloader/api?command=" + cmd, param).then(function (data) {
        that.json_display(data);
        that.return_terminal_input(cmd, data);
        that.return_action_handler(cmd, data);
    });
}

downloader_web_block.prototype.json_display = function (json) {
    let that = this;
    let jsonArea = $('#json_area');
    let old_text = jsonArea.text();
    
    // Format the JSON with tab indentation
    let formattedJson = JSON.stringify(json, null, '\t');
    if (old_text !== '') {
        formattedJson = old_text + '\n' + formattedJson;
    }

    // Update the text content of json_area
    jsonArea.text(formattedJson);

    // Scroll to the bottom of the json_area element
    jsonArea.scrollTop(jsonArea[0].scrollHeight);
};

downloader_web_block.prototype.terminal_display = function (json) {
    let that = this;
    let terminalArea = $('#terminal_area');
    let old_text = terminalArea.text();
    
    // Format the JSON with tab indentation
    let formattedJson = JSON.stringify(json, null, '\t');
    if (old_text !== '') {
        formattedJson = old_text + '\n' + formattedJson;
    }

    // Update the text content of json_area
    terminalArea.text(formattedJson);

    // Scroll to the bottom of the json_area element
    terminalArea.scrollTop(terminalArea[0].scrollHeight);
};

downloader_web_block.prototype.return_action_handler = function (cmd, in_json) {
    let that = this;
    if (cmd == 'local_path_tree') {
        if ('path_tree' in in_json) {
            let folder_tag_list = in_json['path_tree'];
            that.fill_folder_tag_container(folder_tag_list);
        }
        if ('file_tag_relation' in in_json) {
            let tag_list = in_json['file_tag_relation']['tag_list'];
            that.fill_tag_container(tag_list);
            that.tag_list = tag_list;
            that.file_tag_relation = in_json['file_tag_relation']['file_json'];
        }
        let file_container = $('#type_file_container');
        file_container.empty();
    }
    else if (cmd == 'local_path_tag_tree') {
        if ('path_tree' in in_json) {
            let path_list = in_json['path_tree'];
            that.fill_file_container(path_list);
            that.fill_tag_container(that.tag_list);
        }
        
    }
    else if (cmd == 'add_tag') {

    }
}

downloader_web_block.prototype.fill_tag_container = function (tag_list) {
    let that = this;
    let tag_container = $('#type_tag_container');
    tag_container.empty();
    for (let i = 0; i < tag_list.length; i++) {
        let tag_button = $(`<button class="grid_tag_button" value="${tag_list[i]}">` + tag_list[i] + `</button>`);
        tag_container.append(tag_button);
    }
    $('.grid_tag_button').click(function () {
        let selected_tag = $(this).val();
        if (that.selected_file == '') {
            alert('请先选择文件');
            return;
        }
        if (!(that.selected_file in that.file_tag_relation)){
            that.file_tag_relation[that.selected_file] = []
        }
        if (that.file_tag_relation[that.selected_file].includes(selected_tag)) {
            let index = that.file_tag_relation[that.selected_file].indexOf(selected_tag);
            that.file_tag_relation[that.selected_file].splice(index, 1);
            $(this).css('background-color', '#fafafa');
        }
        else {
            that.file_tag_relation[that.selected_file].push(selected_tag);
            $(this).css('background-color', '#ebebeb');
        }
        that.bind_file_tag();
    });
}

downloader_web_block.prototype.fill_folder_tag_container = function (tag_list) {
    let that = this;
    let folder_tag_container = $('#file_tag_container');
    folder_tag_container.empty();
    for (let i = 0; i < tag_list.length; i++) {
        let folder_name = tag_list[i].split('/').pop();
        let tag_button = $(`<button class="grid_folder_tag_button" value="${tag_list[i]}">` + folder_name + `</button>`);
        folder_tag_container.append(tag_button);
    }
    $('.grid_folder_tag_button').click(function () {
        $('.grid_folder_tag_button').css('background-color', '#fafafa');
        $(this).css('background-color', '#dedede');
        let folder_tag = $(this).val();
        that.current_selected_folder_tag = folder_tag;
        that.select_type_folder_tag(folder_tag);
        
    });
}

downloader_web_block.prototype.fill_file_container = function (file_list) {
    let that = this;
    let file_container = $('#type_file_container');
    file_container.empty();
    for (let i = 0; i < file_list.length; i++) {
        let file_base_name = file_list[i].split('/').pop();
        let file_pure_name = file_base_name.split('.')[0];
        let folder_tag_name = that.current_selected_folder_tag.split('/').pop();
        let icon_url = `/toolbox/rs_icon/${that.current_selected_type}/${folder_tag_name}/icon/${file_pure_name}.jpg`
        let file_button = $(`
        <button class="grid_file_button" value="${file_list[i]}">
            <div style="width:100%;align-content:center;">
                <img src="${icon_url}" style="width:4rem; height:2.2rem;">
            </div>
            <p style="margin:0rem;max-width:100%;overflow-x:hidden;">${file_base_name}</p>
        </button>`);
        file_container.append(file_button);
    }
    $('.grid_file_button').click(function () {
        $('.grid_tag_button').css('background-color', '#fafafa');
        $('.grid_file_button').css('background-color', '#fafafa');
        $(this).css('background-color', '#ebebeb');
        let selected_file = $(this).val();
        that.selected_file = selected_file;
        that.prebind_file_tag(selected_file);
    });
}

downloader_web_block.prototype.bind_file_tag = function () {
    let that = this;
    let socket_message = {
        'cmd': 'bind_tag',
        'content': {
            "relation":that.file_tag_relation,
            "resource_type":that.current_selected_type
        }
    }
    that.my_socket.send(JSON.stringify(socket_message));
}

downloader_web_block.prototype.prebind_file_tag = function (file_path) {
    let that = this;
    if (file_path in that.file_tag_relation) {
        let tag_list = that.file_tag_relation[file_path];
        for (let i = 0; i < tag_list.length; i++) {
            $(`.grid_tag_button[value="${tag_list[i]}"]`).css('background-color', '#ebebeb');
        }
    }
}

downloader_web_block.prototype.user_terminal_input = function (cmd, content) {
    let that = this;
    let new_text = "USER INPUT=> "
    let terminalArea = $('#terminal_area');
    let old_text = terminalArea.text();
    let t_text = '';
    if (cmd == 'test_connection') {
        new_text += '连接测试 URL - ' + content['url'];
    }
    else if (cmd == 'local_path_check') {
        new_text += '本地路径检查 PATH - ' + content['path'];
    }
    else if (cmd == 'local_path_tree') {
        new_text += '本地路径树获取 PATH - ' + content['path'];
    }
    else if (cmd == 'start_upload') {
        new_text += '开始上传 PATH - ' + content['path'];
    }
    else if (cmd == 'add_tag') {
        new_text += '添加标签 NAME - ' + content['tag_name'];
    }
    else if (cmd == 'local_path_tag_tree') {
        new_text += '本地路径标签树获取 PATH - ' + content['path'];
    }
    else if (cmd == 'bind_tag') {
        new_text += '绑定标签';
    }
    else {
        new_text += '未知命令';
    }
    if (old_text !== '') {
        t_text = old_text + '\n' + new_text;
    }
    else {
        t_text = new_text;
    }
    terminalArea.text(t_text);
    terminalArea.scrollTop(terminalArea[0].scrollHeight);
}

downloader_web_block.prototype.return_terminal_input = function (cmd, json) {
    let that = this;
    let new_text = "CONSOLE INPUT=> "
    let terminalArea = $('#terminal_area');
    let old_text = terminalArea.text();
    let t_text = '';
    if (cmd == 'test_connection') {
        if (json['status'] == 0) {
            new_text += '连接失败';
        }
        else {
            new_text += '连接成功';
        }
    }
    else if (cmd == 'local_path_check') {
        if (json['status'] == 0) {
            new_text += '输入路径不存在';
        }
        else {
            new_text += '输入路径正常';
        }
    }
    else if (cmd == 'local_path_tree') {
        if (json['status'] == 0) {
            new_text += '路径树获取失败';
        }
        else {
            new_text += '路径树获取成功';
        }
    }
    else if (cmd == 'start_upload') {
        if (json['status'] == 0) {
            new_text += '上传失败';
        }
        else {
            new_text += '上传成功';
        }
    }
    else if (cmd == 'add_tag') {
        if (json['status'] == 0) {
            new_text += '添加标签失败';
        }
        else {
            new_text += '添加标签成功';
        }
    }
    else if (cmd == 'bind_tag') {
        if (json['status'] == 0) {
            new_text += '绑定标签失败';
        }
        else {
            new_text += '绑定标签成功';
        }
    }
    else if (cmd == 'local_path_tag_tree') {
        if (json['status'] == 0) {
            new_text += '路径标签树获取失败';
        }
        else {
            new_text += '路径标签树获取成功';
        }
    }
    else {
        new_text += '未知命令';
    }
    if (old_text !== '') {
        t_text = old_text + '\n' + new_text;
    }
    else {
        t_text = new_text;
    }
    terminalArea.text(t_text);
    terminalArea.scrollTop(terminalArea[0].scrollHeight);
}

downloader_web_block.prototype.init_web_socket = function () {
    const RECONNECT_DELAY = 8000;  // 5 seconds
    let that = this;

    function connect() {
        let domain = window.location.hostname;
        let port = window.location.port;

        let fullAddress = domain + (port ? ':' + port : '');

        // Using this fullAddress in WebSocket URL:
        let protocolPrefix = (window.location.protocol === "https:") ? "wss://" : "ws://";
        let socketURL = protocolPrefix + fullAddress + "/toolbox/tool_downloader/websocket/dd";

        that.my_socket = new WebSocket(socketURL);

        that.my_socket.onopen = function (event) {
            console.log("WebSocket opened: ", event);
            let initialData = {'status':1, 'cmd':'init'};
            that.my_socket.send(JSON.stringify(initialData));
        };

        that.my_socket.onmessage = function (event) {
            console.log("Received: ", event.data);
            let rt_data = JSON.parse(event.data);
        };

        that.my_socket.onerror = function (error) {
            console.log(`WebSocket Error: ${error}`);
        };

        that.my_socket.onclose = function (event) {
            if (event.wasClean) {
                console.log(`WebSocket closed cleanly, code=${event.code}, reason=${event.reason}`);
            } else {
                console.log('WebSocket connection died');
            }

            // Schedule a reconnection attempt
            setTimeout(() => {
                console.log("Attempting to reconnect...");
                connect();
            }, RECONNECT_DELAY);
        };
    }

    // Call the connect function to establish the initial connection
    connect();
}