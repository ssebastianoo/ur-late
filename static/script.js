async function deleteMember(group_id, member) {
  await fetch('/api/v1/members/delete/', {
    headers: { 'Content-Type': 'application/json' },
    method: 'POST',
    body: JSON.stringify({ "group_id": group_id, "member": member })
  });
  await displayGroups();
}

async function addMember(group_id) {
  member = document.getElementById(`${group_id}_member`).value;
  if (!member) {
    return;
  };
  await fetch('/api/v1/members/create/', {
    headers: { 'Content-Type': 'application/json' },
    method: 'POST',
    body: JSON.stringify({ "group_id": group_id, "member": member })
  });
  await displayGroups();
}

async function deleteLate(group, member, late) {
  await fetch('/api/v1/lates/delete/', {
    headers: { 'Content-Type': 'application/json' },
    method: 'POST',
    body: JSON.stringify({"group_id": group, "member": member, "late": late })
  });
  await displayGroups();
}

async function addLate(group_id, member) {
  late = document.getElementById(`${group_id}_${member}_late`).value;
  date = document.getElementById(`${group_id}_${member}_date`).value;
  if (!late) {
    return;
  } else if (!date) {
    return;
  };
  await fetch('/api/v1/lates/create/', {
    headers: { 'Content-Type': 'application/json' },
    method: 'POST',
    body: JSON.stringify({ "group_id": group_id, "member": member, "date": date, "late": late })
  });
  await displayGroups();
};

async function createGroup() {
  var group_name_input = document.getElementById("group_name");
  if (!group_name_input.value) {
    return;
  } else {
    group_name = group_name_input.value;
  };
  await fetch('/api/v1/groups/create/', {
    headers: { 'Content-Type': 'application/json' },
    method: 'POST',
    body: JSON.stringify({ "name": group_name })
  });
  await displayGroups();
  document.getElementById("group_name").value = "";
}

async function deleteGroup(group_id) {
  await fetch('/api/v1/groups/delete/', {
    headers: { 'Content-Type': 'application/json' },
    method: 'POST',
    body: JSON.stringify({ "group_id": group_id })
  });
  await displayGroups();
}

async function displayGroups() {
  var groups = document.getElementById("groups");
  res = await fetch('/api/v1/groups/display/', {
    method: 'GET',
  });
  groups.innerHTML = "";
  if (res.status === 404) {
    groups.innerHTML = "<p>:( you don't have any group</p>"
  } else {
    data = await res.json();
    for (let group in data) {
      var div = document.createElement("div");
      var groupName = document.createElement("h3");
      groupName.innerText = data[group]["name"];
      div.appendChild(groupName);

      var delete_group = document.createElement("button");
      delete_group.onclick = function () { deleteGroup(group) };
      delete_group.type = "submit";
      delete_group.innerText = "delete";
      div.appendChild(delete_group);

      for (let member in data[group]["members"]) {
        var member_name = document.createElement("p")
        member_name.innerText = member;
        div.appendChild(member_name);
        delete_member = document.createElement("button");
        delete_member.onclick = function () { deleteMember(group, member) };
        delete_member.type = "submit";
        delete_member.innerText = "delete";
        div.appendChild(delete_member);
        var ul = document.createElement("ul");
        for (let date_id in data[group]["members"][member]) {
          var date = data[group]["members"][member][date_id]
          var li = document.createElement("li");
          li.innerHTML = `<p>Date: ${date['date']} Late: ${date['late']}</p>`;
          delete_date = document.createElement("button");
          delete_date.onclick = function () { deleteLate(group, member, date_id) };
          delete_date.type = "submit";
          delete_date.innerText = "delete";
          li.appendChild(delete_date);
          ul.appendChild(li);
        };
        div.appendChild(ul);
        inputs = document.createElement("div");
        inputs.innerHTML = `<input id="${group}_${member}_date" type="text" placeholder="date" name="date">\n<input id="${group}_${member}_late" type="text" placeholder="late" name="late">\n<button onclick="addLate('${group}', '${member}')">add late</button>`
        div.appendChild(inputs);
      }
      var member_field = document.createElement("div")
      member_field.innerHTML = `<input type="text" id="${group}_member" name="member" placeholder="member">\n<button type="submit" onclick="addMember('${group}')">add member</button>`;
      div.appendChild(member_field);
      groups.appendChild(div);
    }
  }
}