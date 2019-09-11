<template>
  <div id="app">
    <h1>Hello World !</h1>
    <div class="full-width center-content">
      <hello name="World2" />
    </div>
    <ol>
        <todo-item
          v-for="item in groceryList"
          v-bind:todo="item"
          v-bind:key="item.id"
        ></todo-item>
    </ol>
    <input type="text" v-model="userq" />
    <awesome-button v-bind:tlist="groceryList" :userq="userq"></awesome-button>

    <h1>Your IP is {{ ip }}</h1>
    <input type="text" v-model="input.firstname" placeholder="First Name" />
    <input type="text" v-model="input.lastname" placeholder="Last Name" />
    <button v-on:click="sendData()">Send</button>
    <br />
    <br />
    <textarea>{{ response }}</textarea>
    
  </div>
</template>

<script>
import Hello from '../components/Hello.vue'
import axios from "axios";
export default {
  name: "App",
  components: {
    Hello
  },
  data() {
    return {
        groceryList: [
          { id: 0, text: 'Vegetables' },
          { id: 1, text: 'Cheese' },
          { id: 2, text: 'Whatever else humans are supposed to eat' }
        ],
        userq :'',
        ip: "",
        input: {
            firstname: "",
            lastname: ""
        },
        response: ""
   };
 },
 mounted() {
    axios({ method: "GET", "url": "https://httpbin.org/ip" }).then(result => {
        this.ip = result.data.origin;
    }, error => {
        console.error(error);
    });
 },
    methods: {
        sendData() {
            axios({ method: "POST", "url": "https://httpbin.org/post", "data": this.input, "headers": { "content-type": "application/json" } }).then(result => {
                this.response = result.data;
            }, error => {
                console.error(error);
            });
        }
    }
}
</script>

        methods: { }
    }
</script>

<style>
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-top: 20px;
}

.input {
  width: 50%;
  border: 1px solid #ddd;
  color: #333;
  background: #eee;
  padding: 6px;
  border-radius: 4px;
}
</style>


