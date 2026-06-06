fetch("/api/learned_words").then(response => response.json()).then(data => {
    let box = document.getElementById("learnedWords")
    box.innerHTML = ""
    data.words.forEach(word => {
        box.innerHTML += `<li>${word}</li>`
    })
})

document.getElementById("logoutbtn").addEventListener('click', function(){
    window.location.href= "/logout";
})

document.getElementById("searchBtn").addEventListener("click", async() => {
    let word = document.getElementById("wordInput").value;

document.getElementById("spinner").style.display = "block";
document.getElementById("resultBox").innerHTML= "";

    let res = await fetch("/api", {
        method : "POST",
        headers : {
            "Content-type": "application/json"
        },
        body : JSON.stringify({ text : word })
    });
    let data = await res.json();

document.getElementById("spinner").style.display="none";

if (data.error){
    document.getElementById("resultBox").innerHTML = `<p style="color:red">${data.error}</p>`;
    return;
}
let box = document.getElementById("resultBox");

// reset animation
box.classList.remove("show");

// small delay to allow reset
setTimeout(() => {
    box.innerHTML = data.html;
    box.classList.add("show"); // trigger animation
}, 50);

let learnedDiv = document.getElementById("learnedWords");
    learnedDiv.innerHTML = "";

    data.learned_words.forEach(w => {
        let li = document.createElement("li");
        li.textContent = w;
        learnedDiv.appendChild(li);
    });
});


