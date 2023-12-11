'use strict';
function downloader_web_block() {
    this.selected_type = '';
    this.target_url = '';
    this.target_path = '';
}

downloader_web_block.prototype.init = function () {
    var that = this;
    that.init_layout();
    that.init_listener();
}

downloader_web_block.prototype.init_layout = function () {
    let that = this;
    let body_content = `
    <div style="display:flex; height:100%; width:100%; justify-content:center; align-items:center;">
        <div style="height:35rem; width:60rem; border: 2px solid #777; display:flex;padding:0.3rem;border-radius:0.4rem; ">
            <div style="height:100%; width:25%; display:flex; flex-direction:column; padding:0.2rem;">
                <div style="width:95%; border: 1px solid #aaa;border-radius:0.4rem; padding:0.2rem;display:inline-block;">
                    <input id="target_url_add" type="text" class="dld_input" placeholder="URL" style="width:95%;">
                    <button id="ls_test_connection" class="dld_btn" style="margin-top:0.2rem;width:100%;">test connection</button>
                </div>
                <div style="width:95%; border: 1px solid #aaa;border-radius:0.4rem; padding:0.2rem;display:inline-block;margin-top:0.8rem;">
                    <input id="target_path_id" type="text" class="dld_input" placeholder="LOCAL PATH" style="width:95%;">
                    <button id="ls_confirm" class="dld_btn" style="margin-top:0.2rem;width:100%;">confirm</button>
                    <button id="ls_find_localpath" class="dld_btn" style="margin-top:0.2rem;width:100%;">本地路径树获取</button>
                </div>
                
                <button id="ls_start_upload" class="dld_btn" style="margin-top:0.6rem;">开始上传</button>
            </div>
            
            <div style="height:100%; width:75%; display:flex; flex-direction:column;padding:0.2rem;">
                <div style="height:35%; width:98%; border: 1px solid #aaa;border-radius:0.4rem;padding:0.3rem;">
                    <textarea id="json_area" style="height:100%; width:100%;resize:none;border:none;background-color:#fff;" disabled></textarea>
                </div>
                <div style="height:59%; width:98%; margin-top:1%; border: 1px solid #333;background-color:#222; border-radius:0.2rem;padding:0.3rem;">
                    <textarea id="terminal_area" style="color:#fff;height:100%; width:100%;resize:none;border:none;background-color:#222;"disabled></textarea>
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
    $('#ls_find_localpath').click(function () {
        that.test_path('local_path_tree');
    });
    $('#ls_start_upload').click(function () {
        that.test_path('start_upload');
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
    // $.ajax({
    //     url: that.target_url,
    //     type: 'GET',
    //     success: function (data) {
    //         alert('连接成功');
    //     },
    //     error: function (err) {
    //         alert('连接失败');
    //     }
    // });
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

downloader_web_block.prototype.resource_action = function (cmd, content) {
    let that = this;
    let param = { 'type': cmd, 'content': content };
    that.user_terminal_input(cmd, content);
    that.vm_ajax_util.load_json_post_fetch("/toolbox/tool_downloader/api?command=" + cmd, param).then(function (data) {
        that.json_display(data);
        that.return_terminal_input(cmd, data);
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