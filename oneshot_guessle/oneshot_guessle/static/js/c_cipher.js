const title_heading = [
    "شفرة الهلال",
    "Crescent Cipher",
    "Hilal Şifresi",
    "Chiffre du Croissant",

]

const title_year = [
    "1447",
    "10110100111",
    "١٤٤٧",
    "MCMXLVII",
    "&lt;y&gt;1447&lt;/y&gt;",
    "&lt;sene&gt;1447&lt;/sene&gt;",
    "&lt;año&gt;1447&lt;/año&gt;",
    ".---- ....- ....- --...",
    " سنة 1447 ",
    "١٠١١٠٠١٠٠١١١",
    "&lt;سنة&gt;١٤٤٧&lt;/سنة&gt;",
]

// Function to pick random heading and year
function getRandomTitlePair() {
    const randomHeading = title_heading[Math.floor(Math.random() * title_heading.length)];
    const randomYear = title_year[Math.floor(Math.random() * title_year.length)];
    return {
        heading: randomHeading,
        year: randomYear
    };
}

// Get random title pair on page load and update DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded event fired');
    
    const titlePair = getRandomTitlePair();
    console.log('Random title pair:', titlePair);
    
    const headingElement = document.getElementById('heading-element');
    const yearElement = document.getElementById('year-element');
    
    console.log('Heading element:', headingElement);
    console.log('Year element:', yearElement);
    
    if (headingElement) {
        headingElement.innerHTML = titlePair.heading;
        console.log('Heading set to:', titlePair.heading);
    } else {
        console.error('heading-element not found!');
    }
    
    if (yearElement) {
        yearElement.innerHTML = titlePair.year;
        console.log('Year set to:', titlePair.year);
    } else {
        console.error('year-element not found!');
    }
});