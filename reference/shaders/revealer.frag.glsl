uniform vec3 uColor1;
uniform vec3 uColor2;
uniform float uClicked;

float r(in vec2 p)
{
    return fract(cos(p.x*42.98 + p.y*43.23) * 1127.53);
}

float n(in vec2 p)
{
    vec2 fn = floor(p);
    vec2 sn = smoothstep(vec2(0), vec2(1), fract(p));
    
    float h1 = mix(r(fn), r(fn + vec2(1,0)), sn.x);
    float h2 = mix(r(fn + vec2(0,1)), r(fn + vec2(1)), sn.x);
    return mix(h1 ,h2, sn.y);
}

float noise(in vec2 p)
{
    return n(p/32.) * 0.58 +
           n(p/16.) * 0.2  +
           n(p/8.)  * 0.1  +
           n(p/4.)  * 0.05 +
           n(p/2.)  * 0.02 +
           n(p)     * 0.0125;
}

void main() {

  float t = uClicked;

  float progress = smoothstep(t + .1, t - .1, noise(gl_FragCoord.xy * 0.4));

  vec4 c = mix(vec4(uColor1, progress), vec4(uColor2, 1.), progress);

  gl_FragColor = c;
}
