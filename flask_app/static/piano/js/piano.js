const keys  = document.querySelectorAll(".key"), 
      note  = document.querySelector(".nowplaying"),
      hints = document.querySelectorAll(".hints");
      doom  = 0;
var   array = [];



const scary = "https://orangefreesounds.com/wp-content/uploads/2020/09/Creepy-piano-sound-effect.mp3?_=1"

const sound = {65:"http://carolinegabriel.com/demo/js-keyboard/sounds/040.wav",
               87:"http://carolinegabriel.com/demo/js-keyboard/sounds/041.wav",
               83:"http://carolinegabriel.com/demo/js-keyboard/sounds/042.wav",
               69:"http://carolinegabriel.com/demo/js-keyboard/sounds/043.wav",
               68:"http://carolinegabriel.com/demo/js-keyboard/sounds/044.wav",
               70:"http://carolinegabriel.com/demo/js-keyboard/sounds/045.wav",
               84:"http://carolinegabriel.com/demo/js-keyboard/sounds/046.wav",
               71:"http://carolinegabriel.com/demo/js-keyboard/sounds/047.wav",
               89:"http://carolinegabriel.com/demo/js-keyboard/sounds/048.wav",
               72:"http://carolinegabriel.com/demo/js-keyboard/sounds/049.wav",
               85:"http://carolinegabriel.com/demo/js-keyboard/sounds/050.wav",
               74:"http://carolinegabriel.com/demo/js-keyboard/sounds/051.wav",
               75:"http://carolinegabriel.com/demo/js-keyboard/sounds/052.wav",
               79:"http://carolinegabriel.com/demo/js-keyboard/sounds/053.wav",
               76:"http://carolinegabriel.com/demo/js-keyboard/sounds/054.wav",
               80:"http://carolinegabriel.com/demo/js-keyboard/sounds/055.wav",
               186:"http://carolinegabriel.com/demo/js-keyboard/sounds/056.wav"};

// ------------------------------------------------------------------------
// Listens for a change to the pressed key, and updates the hidden phrase.
// ------------------------------------------------------------------------
note.addEventListener('DOMSubtreeModified', function(){
  const result = note.innerHTML;
  array += result;

  if (array.length > 8) {
    array = array.slice(1,9);
    }
  console.log('The array'); console.log(array);

  if (array === "WESEEYOU" && doom === 0){
    doom = 1;
    document.querySelector(".bkgdc").style.opacity=0;
    document.querySelector(".bgimg").style.opacity=1;
    document.querySelector(".keys").style.opacity=0;


    const audio = new Audio(scary);
    audio.currentTime = 0;
    audio.play();
    document.getElementById("message").innerHTML = "I have awoken."
    } 
});

// ------------------------------------------------------------------------
// We use an e here because we selected a set of KEYS!
// ------------------------------------------------------------------------
function playNote(e) {
  //console.log(e);
  
  if (doom === 1) return;

  console.log(e.keyCode);

  const key = document.querySelector(`.key[data-key="${e.keyCode}"]`);
  if (!key) return;
  const keyPressed = key.firstChild.innerHTML;

  key.classList.add("playing");
  note.innerHTML = keyPressed;

  // play the audio
  const audio = new Audio(sound[e.keyCode]);
  audio.currentTime = 0;
  audio.play();

}

function removeTransition(e) {
  if (e.propertyName !== "transform") return;
  this.classList.remove("playing");
}

// -------------------------------------------------------------------------
// FOR THE HINTS
// --------------------------------------------------------------------------
function hintsOn(e, index) {
  //console.log(e)
  console.log(e.fromElement.id)
  const key = document.querySelector(`.key[data-key="${e.fromElement.id}"]`);
  key/
  console.log(key)
  if (!key) return;

  key.setAttribute("background", "red")
  key.setAttribute("style", "transition-delay:" + 50 + "ms");
}

//hints.forEach(hintsOn);
keys.forEach(key => key.addEventListener("transitionend", removeTransition));

//This is what binds 'e'.
window.addEventListener("keydown", playNote);
window.addEventListener("mouseover", hintsOn);


