function hide_and_show(tohide, toshow) {
    x = document.querySelector(tohide);
    x.style.width = '0';
    x.style.display = 'none';
    
    y = document.querySelector(toshow);
    y.style.width = '100%';
    y.style.display = 'flex';
};

function get_requests() {
    var e = document.getElementById("SelectShowType");
    var showtype = e.options[e.selectedIndex].value;

    if (showtype == 'Normal' || showtype == 'Anime') {
        document.querySelector('#select-type').style.color = 'black';
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                console.log(this.response);
                document.querySelector('.request-results').innerHTML = this.response['html'];
                document.querySelector('.post-request').style.display = 'flex';
            }
            else if (this.readyState == 4 && this.status != 200) {
                console.log(this.response);
                document.querySelector('#request-error').innerHTML = this.response['html'];
            }
        };
        
        var query = document.getElementById('request-search').value;
        req_type = showtype;
        req_choice = 0;
        req_name = '';

        xhttp.open('GET', `/getrequest/${showtype}/${query}`, true);
        xhttp.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        xhttp.responseType = 'json';
        xhttp.send();
    }
    else {
        document.querySelector('#select-type').style.color = 'red';
    }
};

var req_choice = 0;
var req_type = '';
var req_name = '';

function change_request(id, num) {
    var animelist = document.querySelectorAll('.new-request-indv');
    for (i=0; i< animelist.length; i++) {
        animelist[i].style.backgroundColor = "";
        animelist[i].style.border = "";
    }
    document.querySelector(id).style.backgroundColor = '#dee3df';
    document.querySelector(id).style.border = '1px black solid';
    req_choice = num;
    req_name = document.querySelector(id).querySelector('h3').innerHTML;
};

function post_request() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            loadcontent('/requests', '.content', true);
        }
        else if (this.readyState == 4 && this.status != 200) {
            console.log(this.response);
            document.querySelector('#request-error').innerHTML = this.response['html'];
        }
    };
    var data = new FormData(document.querySelector('#csrf_form'));
    data.append('showtype', req_type);
    data.append('choice', req_choice);
    
    xhttp.open('POST', "/makerequest", true);
    xhttp.responseType = 'json';
    xhttp.send(data);
};

function make_request() {
    if (req_choice == 0) {
        document.querySelector('#request-error').innerHTML = 'Please Select A Show!';
    }
    else {
        var r = confirm(`Confirm Request : ${req_name}?`);
        if  (r == true) {
            post_request();
        }
    }   
};

function toggle_vote(element) {
    
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            console.log(this.response.text);
            var votecount = element.parentNode.querySelector('#votenum');

            if (element.className == 'voted') {
                votecount.innerHTML = parseInt(votecount.innerHTML, 10) - 1;
            }
            else {
                votecount.innerHTML = parseInt(votecount.innerHTML, 10) + 1;
            }   
            element.classList.toggle("voted");
        }
    }
    xhttp.open('POST', '/voterequest', true);
    var data = new FormData();
    data.append('requestid', element.parentNode.id)
    xhttp.setRequestHeader('X-CSRFToken', token);
    xhttp.send(data);

};

function delete_request(element) {
        var r = confirm('Confirmm Deletion?');
        if  (r == true) {
            var xhttp = new XMLHttpRequest();
            xhttp.onreadystatechange = function () {
                if (this.readyState == 4 && this.status == 200) {
                    loadcontent('/requests', '.content', true);
                }
            }
            xhttp.open('POST', '/deleterequest', true);
            var data = new FormData();
            data.append('requestid', element.parentNode.parentNode.id)
            xhttp.setRequestHeader('X-CSRFToken', token);
            xhttp.send(data);
        }
};

var request_query = '';

function search_requests(page) {
    var e = document.getElementById("SelectRequestType");
    var requesttype = e.options[e.selectedIndex].value;
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log(this.response);
            document.querySelector('.the-requests').innerHTML = this.response['html'];
        };
    };
    xhttp.open('GET', `/searchrequest/${requesttype}/${request_query}/${page}`, true);
    xhttp.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhttp.responseType = 'json';
    xhttp.send();

};

function pre_search(page) {
    request_query = document.querySelector('#search-requests').value;
    search_requests(page);
};
