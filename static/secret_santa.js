let addBtn = document.querySelector("#push_to_add")
let submitBtn = document.querySelector("#submit")

let repeatingSection = document.querySelector('#repeating_section');

addBtn.onclick = e => {
    e.preventDefault();

    let repeatingForm = `
        <form action="">

        <label for="name">Name</label>
        <input name="name" id="name"/>

        <label for="phone">Phone Number</label> <br>
        <input type="tel" name="phone" id="phone"/> <br>

        <label for="notes">Notes</label>
        <textarea name="notes" id="notes" placeholder="Add notes about shipping, likes, dislikes, etc..."></textarea>
        
        <label for="group1">Group 1 (Optional)</label>
        <input name="group1" id="group1"/>
        <label for="group2">Group 2 (Optional)</label>
        <input name="group2" id="group2"/>
        <label for="group3">Group 3 (Optional)</label>
        <input name="group3" id="group3"/>
        <button type="button" id="remove">Remove</button>
        </form>
        <br/>
        <br/>
    `;
    let newForm = document.createElement('div');
    newForm.innerHTML = repeatingForm;
    newForm.className = "individual"
    window.intlTelInput(newForm.querySelector("#phone"), {
        utilsScript: "intl-tel-input/js/utils.js"
    });
    newForm.querySelector("#remove").onclick = () => {
        repeatingSection.removeChild(newForm);
    }
    repeatingSection.appendChild(newForm);
}

addBtn.click()

submitBtn.onclick = () => {
    let groupsSet = new Set()
    let individualsArray = []

    let validated = true;

    Array.from(repeatingSection.children).forEach((child) => {
        if (child.className === "individual") {
            let groups = [];
            let group1 = child.querySelector("#group1").value;
            if (group1.length > 0) {
                groupsSet.add(group1)
                groups.push(group1)
            }
            let group2 = child.querySelector("#group2").value;
            if (group2.length > 0) {
                groupsSet.add(group2)
                groups.push(group2)
            }
            let group3 = child.querySelector("#group3").value;
            if (group3.length > 0) {
                groupsSet.add(group3)
                groups.push(group3)
            }

            let name = child.querySelector("#name").value;
            if (name.length === 0) {
                alert("Name cannot be empty!");
                validated = false;
                return
            }
            let intlTelInstance = window.intlTelInputGlobals.getInstance(child.querySelector("#phone"));
            if (!intlTelInstance.isValidNumber()) {
                alert(`Invalid phone number! Provided: ${child.querySelector("#phone").value}`);
                validated = false;
                return
            }
            let phone = intlTelInstance.getNumber();
            let notes = child.querySelector("#notes").value;

            individualsArray.push({
                name: name.toString(),
                contact: phone.toString(),
                notes: notes.toString(),
                groups: groups
            });
        }
    });

    if (!validated) {
        return
    }

    let groupsArray = Array.from(groupsSet)
    individualsArray.forEach((e) => {
        e.groups = e.groups.map((e) => groupsArray.indexOf(e))
    })

    let dataObject = {
        data: {
            groups: groupsArray.map((e) => {
                return {name: e}
            }),
            individuals: individualsArray
        }
    }

    fetch('/solve', {
        method: 'POST',
        body: JSON.stringify(dataObject),
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(resp => resp.json())
        .then(respData => {
            if (respData.statusCode !== 200) {
                alert(respData.message)
                return
            }
            console.log(respData)
            let modal = document.querySelector("#notifyModal")

            // When the user clicks on <span> (x), close the modal
            modal.querySelector(".close").onclick = function () {
                modal.style.display = "none";
            }

            modal.querySelector("#notify").onclick = () => {
                modal.querySelector("#notify").onclick = () => {};
                fetch('/notify', {
                    method: 'POST',
                    body: JSON.stringify(respData),
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                    .then(resp => resp.json())
                    .then(respData => {
                        if (respData.statusCode !== 200) {
                            alert(respData.message)
                        } else {
                            alert("Successfully sent notifications!")
                        }
                        modal.style.display = "none";
                    })
            }
            modal.style.display = "block";
        })
}