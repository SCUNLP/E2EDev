let pianoKeys = document.querySelectorAll(".piano-keys .key[data-testid^='piano-key']"); 
let volumeSlider = document.querySelector("[data-testid='volume-slider']");
let keysCheckbox = document.querySelector("[data-testid='show-keys-checkbox']");

let allKeys = [],
audio = new Audio("tunes/a.wav");

let playTune = (key) => {
    audio.src = `tunes/${key}.wav`; 
    audio.play();  
    
    let clickedKey = document.querySelector(`[data-key="${key}"]`); 
    clickedKey.classList.add("active");  
    setTimeout(() => {  
        clickedKey.classList.remove("active");
    }, 150);
}

pianoKeys.forEach((key) => {
    allKeys.push(key.dataset.key);
    
    key.addEventListener("click", () => playTune(key.dataset.key));
});

let handleVolume = (e) => {
    audio.volume = e.target.value;  
}

let pressedKey = (e) => {
    if (allKeys.includes(e.key)) {
        playTune(e.key);
    }
}

let showhideKeys = () => {
    pianoKeys.forEach(key => key.classList.toggle("hide"));
}

document.addEventListener("keydown", pressedKey);
volumeSlider.addEventListener("input", handleVolume);
keysCheckbox.addEventListener("click", showhideKeys);
