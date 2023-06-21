/* Project specific Javascript goes here. */
function get_definition(word){

    const userAction = async () => {
        const response = await fetch('https://api.dictionaryapi.dev/api/v2/entries/en/"${word}"');
        const myJson = await response.json(); //extract JSON from the http response
        // do something with myJson
        console.log(myJson);
      }


}