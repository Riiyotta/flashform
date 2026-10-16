varying vec2 vUv;
uniform float u_time;
uniform float u_timeOffset;
uniform vec3 u_color1;
uniform vec3 u_color2;
uniform vec2 u_mousePosition;

vec3 rgb(float r, float g, float b) {
    return vec3(r / 255., g / 255., b / 255.);
}

void main() {
    vec3 c1 = rgb(u_color1.r, u_color1.g, u_color1.b);
    vec3 c2 = rgb(u_color2.r, u_color2.g, u_color2.b);
    vec3 color = c1;

    vec2 pos = vec2(0.5) - vUv;
    float r = length(pos) * 5.0;
    float a = atan(pos.y, pos.x);
    float count = 3. + u_mousePosition.x * 3.;
    float shape =
        abs(cos(a * (count * 3.) + (u_time  * 0.8 + u_timeOffset))) *
        sin(a * count - (u_time  * 0.8 + u_timeOffset))
    ;

    color = mix(
        color,
        c2,
        r
    );

    color *= 1. + (1. - u_mousePosition.y) * 0.5;

    float alpha = (1. - smoothstep(shape, shape + 0.8, r)) + (1. - smoothstep(shape, shape + 1.5, r)) * 0.2;
    gl_FragColor = vec4(color, alpha);
}
