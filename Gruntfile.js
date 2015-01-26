/**
 * Created by virusdefender on 15/1/25.
 */
module.exports = function(grunt) {
  // Do grunt-related things in here
  // 配置
    grunt.initConfig({

        concat : {
            domop : {
                src: ['static/js/jquery.min.js.js', 'static/js/avalon.min.js', 'statis/js/amazeui.min.js'],
                dest: 'static/js/c1.js'
            }
        },
        uglify : {

            build : {
                src : 'static/js/c1.js',
                dest : 'static/js/c1.min.js'
            }
        }
    });
    // 载入concat和uglify插件，分别对于合并和压缩
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    // 注册任务
    grunt.registerTask('default', ['concat', 'uglify']);
}