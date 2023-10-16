window.onload = function() {
    fetchTags();

    document.getElementById('addTagButton').addEventListener('click', addTag);
}

function fetchTags() {
    fetch('/api/tags')
    .then(response => response.json())
    .then(data => {
        let table = document.getElementById('tagsTable');
        for (let key in data) {
            let row = table.insertRow();
            let cell1 = row.insertCell();
            let cell2 = row.insertCell();
            let cell3 = row.insertCell();
            cell1.innerHTML = key;
            cell2.innerHTML = data[key];
            cell3.innerHTML = '<button onclick="deleteTag(\'' + key + '\', this)">Delete</button>';
        }
    });
}

function addTag() {
    let english = document.getElementById('english').value;
    let chinese = document.getElementById('chinese').value;

    fetch('/api/tags', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({key:english,value:chinese})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            let table = document.getElementById('tagsTable');
            let row = table.insertRow();
            let cell1 = row.insertCell();
            let cell2 = row.insertCell();
            let cell3 = row.insertCell();
            cell1.innerHTML = english;
            cell2.innerHTML = chinese;
            cell3.innerHTML = '<button onclick="deleteTag(\'' + english + '\', this)">Delete</button>';
        } else {
            alert('Failed to add tag');
        }
    });
}

function deleteTag(key, btn) {
    fetch('/api/tags', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({key: key})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove the row from the table
            let row = btn.parentNode.parentNode;
            row.parentNode.removeChild(row);
        } else {
            alert('Failed to delete tag');
        }
    });
}
