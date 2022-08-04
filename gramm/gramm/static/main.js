const app = Vue.createApp({
  delimiters: ["[[", "]]"],
  data() {
    return {
      checked: false,
      tags: [],
    };
  },
  methods: {
    getListTags(){
    fetch("/user_tags/")
      .then(response => response.json())
      .then(data => (this.tags = data));
    },
    hidecont(){
      this.checked = !this.checked;
    },
  },
});
app.mount("#app");

