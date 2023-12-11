export class vm_ajax_util{
    static load_json_post_jquery(strAdress, data) {
        let p = new Promise(function(resolve,reject){
            var xhr = new XMLHttpRequest();
            xhr.open("POST", strAdress, true);
            xhr.setRequestHeader("Content-type","application/json;charset=utf-8");
            xhr.onreadystatechange = function(){
                if (xhr.readyState == 4) {
                    var status = xhr.status;
                    if (status >= 200 && status < 300 || status == 304) {
                        resolve( xhr.responseText);
                    } else {
                        reject( xhr.responseText);
                    }
                }
            }
            xhr.send(data)
        });
        return p;
    }
    static load_json_get_fetch(strAdress) {
        return fetch(strAdress, {
            method: 'GET',
            headers: {
                "Content-type":"application/json;charset=utf-8"
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("HTTP error " + response.status);
            }
            return response.json();
        })
    }

    static load_json_post_fetch(url, data) {
        return fetch(url, {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'
            }, 
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
    
    static load_wwwform_post_jquery(strAdress, data) {
        let p = new Promise(function(resolve,reject){
            var xhr = new XMLHttpRequest();
            xhr.open("POST", strAdress, true);
            xhr.setRequestHeader("Content-type","application/x-www-form-urlencoded");
            xhr.onreadystatechange = function(){
                if (xhr.readyState == 4) {
                    var status = xhr.status;
                    if (status >= 200 && status < 300 || status == 304) {
                        resolve( xhr.responseText);
                    } else {
                        reject( xhr.responseText);
                    }
                }
            }
            xhr.send(data)
        });
        return p;
    }
    static post_form(url,in_new_page,params){
        var form = document.createElement("form");
        form.action = url;
        if(in_new_page == true)
            form.target = "_blank";
        else
            form.target = "_self";
        form.method = "post";
        form.style.display = "none";
        //添加参数
        for(var i in params){
            var opt = document.createElement("textarea");
            opt.name = params[i].name;
            opt.value = params[i].value;
            form.appendChild(opt); 
        }
        document.body.appendChild(form);
        form.submit();
        return form;
    }
}
