import os
import glm
from glm import vec4, vec3, vec2, ivec4, dot

vertex_inputs = []
buffers = {}
vertex_count = 0

def cb(cbidx : int, offset : int):
    name = "cb" + str(cbidx) + "_" + str(offset)
    if name in buffers:
        vector = buffers[name]
        return vec4(vector.x, vector.y, vector.z, vector.w)
    else:
        raise ValueError(f"Buffer {name} not found.")
    
def t(tidx : int, offset : int):
    name = "t" + str(tidx) + "_" + str(offset)
    if name in buffers:
        vector = buffers[name]
        return vec4(vector.x, vector.y, vector.z, vector.w)
    else:
        raise ValueError(f"Buffer {name} not found.")

def init_vertex_input(csv_file_path : str):
    global vertex_inputs, vertex_count
    vertex_count = 0
    vertex_inputs.clear()
    with open(csv_file_path, 'r') as csv_file:
        lines = csv_file.readlines()
    lines0 = lines[0].strip().split(',')
    lines0 = [x.strip().replace('ATTRIBUTE', 'v') for x in lines0]
    datalines = lines[1:]
    vertex_count = len(datalines)
    for dataline in datalines:
        datas = dataline.strip().split(',')
        datas = [float(x.strip()) for x in datas]
        vertex_inputs.append(datas)
    # print(vertex_count, "vertices initialized.")

def init_resources(filename : str):
    global buffers
    buffers.clear()
    # 目前我发现其实压根没用上cb
    # cbuffer_dir = "cb/" + filename
    # for file in os.listdir(cbuffer_dir):
    #     if file.endswith('.csv'):
    #         with open(os.path.join(cbuffer_dir, file), 'r') as csv_file:
    #             lines = csv_file.readlines()[1:]
    #             for idx, line in enumerate(lines):
    #                 data = line.split('"')[1]
    #                 data = data.split(',')
    #                 data = [float(x.strip()) for x in data]
    #                 buffer_name = file[:-4] + "_" + str(idx)
    #                 buffers[buffer_name] = glm.vec4(*data)
    #                 # print(f"Buffer {buffer_name} initialized with data: {data}")
    tbuffer_dir = "t/" + filename
    for file in os.listdir(tbuffer_dir):
        if file.endswith('.csv'):
            with open(os.path.join(tbuffer_dir, file), 'r') as csv_file:
                lines = csv_file.readlines()[1:]
                for idx, line in enumerate(lines):
                    data = line.split(',')[1:]
                    data = [float(x.strip()) for x in data]
                    buffer_name = file[:-4] + "_" + str(idx)
                    buffers[buffer_name] = glm.vec4(*data)
                    # print(f"Buffer {buffer_name} initialized with data: {data}")

def convert_csv(filename : str):
    csv_file_path = "csv/" + filename + ".csv"
    init_vertex_input(csv_file_path)
    init_resources(filename)
    
    csv_content = "VTX,\tIDX,\tPosition.x,\tPosition.y,\tPosition.z\n"
    for i in range(vertex_count):
        position = get_world_position(i)
        VTX = vertex_inputs[i][0]
        IDX = vertex_inputs[i][1]
        csv_content += f"{VTX},\t{IDX},\t{position.x},\t{position.y},\t{position.z}\n"
    with open(filename + ".csv", "w") as output_file:
        output_file.write(csv_content)

def get_world_position(vid : int) -> vec3:
    global vertex_inputs, buffers
    def _v0() -> vec4:
        data = vertex_inputs[vid][2:][0:3]
        return vec4(data[0], data[1], data[2], 1.0)
    def _v1() -> vec3:
        data = vertex_inputs[vid][2:][3:7]
        return vec3(data[0], data[1], data[2])
    def _v2() -> vec4:
        data = vertex_inputs[vid][2:][7:11]
        return vec4(data[0], data[1], data[2], data[3])
    def _v3() -> ivec4:
        data = vertex_inputs[vid][2:][17:21]
        return ivec4(int(data[0]), int(data[1]), int(data[2]), int(data[3]))
    def _v4() -> ivec4:
        data = vertex_inputs[vid][2:][21:25]
        return ivec4(int(data[0]), int(data[1]), int(data[2]), int(data[3]))
    def _v5() -> vec4:
        data = vertex_inputs[vid][2:][25:29]
        return vec4(data[0], data[1], data[2], data[3])
    def _v6() -> vec4:
        data = vertex_inputs[vid][2:][29:33]
        return vec4(data[0], data[1], data[2], data[3])
    def _v7() -> vec2:
        data = vertex_inputs[vid][2:][11:13]
        return vec2(data[0], data[1])
    def _v8() -> vec3:
        data = vertex_inputs[vid][2:][36:39]
        return vec3(data[0], data[1], data[2])
    def _v9() -> vec3:
        data = vertex_inputs[vid][2:][33:36]
        return vec3(data[0], data[1], data[2])
    def _v10() -> vec4:
        data = vertex_inputs[vid][2:][13:17]
        return vec4(data[0], data[1], data[2], data[3])

    v0 = _v0()
    v1 = _v1()
    v2 = _v2()
    v3 = _v3()
    v4 = _v4()
    v5 = _v5()
    v6 = _v6()
    v7 = _v7()
    v8 = _v8()
    v9 = _v9()
    v10 = _v10()
    # 开始逆向
#    0: imul null, r0.xyzw, v3.xyzw, l(3, 3, 3, 3)
    r0 = v3 * ivec4(3, 3, 3, 3)
#    1: ld_indexable(buffer)(float,float,float,float) r1.xyzw, r0.xxxx, t1.xyzw
    r1 = t(1, int(r0.x))
#    2: imad r2.xyzw, v3.xxyy, l(3, 3, 3, 3), l(1, 2, 1, 2)
    r2 = v3.xxyy * ivec4(3, 3, 3, 3) + ivec4(1, 2, 1, 2)
#    3: ld_indexable(buffer)(float,float,float,float) r3.xyzw, r2.xxxx, t1.xyzw
    r3 = t(1, int(r2.x))
#    4: ld_indexable(buffer)(float,float,float,float) r4.xyzw, r2.yyyy, t1.xyzw
    r4 = t(1, int(r2.y))
#    5: ld_indexable(buffer)(float,float,float,float) r5.xyzw, r0.yyyy, t1.xyzw
    r5 = t(1, int(r0.y))
#    6: ld_indexable(buffer)(float,float,float,float) r6.xyzw, r2.zzzz, t1.xyzw
    r6 = t(1, int(r2.z))
#    7: ld_indexable(buffer)(float,float,float,float) r2.xyzw, r2.wwww, t1.xyzw
    r2 = t(1, int(r2.w))
#    8: mul r5.xyzw, r5.xyzw, v5.yyyy
    r5 = r5 * v5.yyyy
#    9: mul r6.xyzw, r6.xyzw, v5.yyyy+
    r6 = r6 * v5.yyyy
#   10: mul r2.xyzw, r2.xyzw, v5.yyyy
    r2 = r2 * v5.yyyy
#   11: mad r1.xyzw, v5.xxxx, r1.xyzw, r5.xyzw
    r1 = v5.xxxx * r1 + r5
#   12: mad r3.xyzw, v5.xxxx, r3.xyzw, r6.xyzw
    r3 = v5.xxxx * r3 + r6
#   13: mad r2.xyzw, v5.xxxx, r4.xyzw, r2.xyzw
    r2 = v5.xxxx * r4 + r2
#   14: ld_indexable(buffer)(float,float,float,float) r4.xyzw, r0.zzzz, t1.xyzw
    r4 = t(1, int(r0.z))
#   15: imad r5.xyzw, v3.zzww, l(3, 3, 3, 3), l(1, 2, 1, 2)
    r5 = v3.zzww * ivec4(3, 3, 3, 3) + ivec4(1, 2, 1, 2)
#   16: ld_indexable(buffer)(float,float,float,float) r6.xyzw, r5.xxxx, t1.xyzw
    r6 = t(1, int(r5.x))
#   17: ld_indexable(buffer)(float,float,float,float) r7.xyzw, r5.yyyy, t1.xyzw
    r7 = t(1, int(r5.y))
#   18: mad r1.xyzw, v5.zzzz, r4.xyzw, r1.xyzw
    r1 = v5.zzzz * r4 + r1
#   19: mad r3.xyzw, v5.zzzz, r6.xyzw, r3.xyzw
    r3 = v5.zzzz * r6 + r3
#   20: mad r2.xyzw, v5.zzzz, r7.xyzw, r2.xyzw
    r2 = v5.zzzz * r7 + r2
#   21: ld_indexable(buffer)(float,float,float,float) r0.xyzw, r0.wwww, t1.xyzw
    r0 = t(1, int(r0.w))
#   22: ld_indexable(buffer)(float,float,float,float) r4.xyzw, r5.zzzz, t1.xyzw
    r4 = t(1, int(r5.z))
#   23: ld_indexable(buffer)(float,float,float,float) r5.xyzw, r5.wwww, t1.xyzw
    r5 = t(1, int(r5.w))
#   24: mad r0.xyzw, v5.wwww, r0.xyzw, r1.xyzw
    r0 = v5.wwww * r0 + r1
#   25: mad r1.xyzw, v5.wwww, r4.xyzw, r3.xyzw
    r1 = v5.wwww * r4 + r3
#   26: mad r2.xyzw, v5.wwww, r5.xyzw, r2.xyzw
    r2 = v5.wwww * r5 + r2
#   27: ult r3.x, l(4), cb0[1].y
    r3.x = 1 if 4 < 8 else 0 # cb0[1].y is 8 maybe
#   28: if_nz r3.x
    if r3.x != 0:
#   29:   imul null, r3.xyzw, v4.xyzw, l(3, 3, 3, 3)
        r3 = v4 * ivec4(3, 3, 3, 3)
#   30:   ld_indexable(buffer)(float,float,float,float) r4.xyzw, r3.xxxx, t1.xyzw
        r4 = t(1, int(r3.x))
#   31:   imad r5.xyzw, v4.xxyy, l(3, 3, 3, 3), l(1, 2, 1, 2)
        r5 = v4.xxyy * ivec4(3, 3, 3, 3) + ivec4(1, 2, 1, 2)
#   32:   ld_indexable(buffer)(float,float,float,float) r6.xyzw, r5.xxxx, t1.xyzw
        r6 = t(1, int(r5.x))
#   33:   ld_indexable(buffer)(float,float,float,float) r7.xyzw, r5.yyyy, t1.xyzw
        r7 = t(1, int(r5.y))
#   34:   mad r4.xyzw, v6.xxxx, r4.xyzw, r0.xyzw
        r4 = v6.xxxx * r4 + r0
#   35:   mad r6.xyzw, v6.xxxx, r6.xyzw, r1.xyzw
        r6 = v6.xxxx * r6 + r1
#   36:   mad r7.xyzw, v6.xxxx, r7.xyzw, r2.xyzw
        r7 = v6.xxxx * r7 + r2
#   37:   ld_indexable(buffer)(float,float,float,float) r8.xyzw, r3.yyyy, t1.xyzw
        r8 = t(1, int(r3.y))
#   38:   ld_indexable(buffer)(float,float,float,float) r9.xyzw, r5.zzzz, t1.xyzw
        r9 = t(1, int(r5.z))
#   39:   ld_indexable(buffer)(float,float,float,float) r5.xyzw, r5.wwww, t1.xyzw
        r5 = t(1, int(r5.w))
#   40:   mad r4.xyzw, v6.yyyy, r8.xyzw, r4.xyzw
        r4 = v6.yyyy * r8 + r4
#   41:   mad r6.xyzw, v6.yyyy, r9.xyzw, r6.xyzw
        r6 = v6.yyyy * r9 + r6
#   42:   mad r5.xyzw, v6.yyyy, r5.xyzw, r7.xyzw
        r5 = v6.yyyy * r5 + r7
#   43:   ld_indexable(buffer)(float,float,float,float) r7.xyzw, r3.zzzz, t1.xyzw
        r7 = t(1, int(r3.z))
#   44:   imad r8.xyzw, v4.zzww, l(3, 3, 3, 3), l(1, 2, 1, 2)
        r8 = v4.zzww * ivec4(3, 3, 3, 3) + ivec4(1, 2, 1, 2)
#   45:   ld_indexable(buffer)(float,float,float,float) r9.xyzw, r8.xxxx, t1.xyzw
        r9 = t(1, int(r8.x))
#   46:   ld_indexable(buffer)(float,float,float,float) r10.xyzw, r8.yyyy, t1.xyzw
        r10 = t(1, int(r8.y))
#   47:   mad r4.xyzw, v6.zzzz, r7.xyzw, r4.xyzw
        r4 = v6.zzzz * r7 + r4
#   48:   mad r6.xyzw, v6.zzzz, r9.xyzw, r6.xyzw
        r6 = v6.zzzz * r9 + r6
#   49:   mad r5.xyzw, v6.zzzz, r10.xyzw, r5.xyzw
        r5 = v6.zzzz * r10 + r5
#   50:   ld_indexable(buffer)(float,float,float,float) r3.xyzw, r3.wwww, t1.xyzw
        r3 = t(1, int(r3.w))
#   51:   ld_indexable(buffer)(float,float,float,float) r7.xyzw, r8.zzzz, t1.xyzw
        r7 = t(1, int(r8.z))
#   52:   ld_indexable(buffer)(float,float,float,float) r8.xyzw, r8.wwww, t1.xyzw
        r8 = t(1, int(r8.w))
#   53:   mad r0.xyzw, v6.wwww, r3.xyzw, r4.xyzw
        r0 = v6.wwww * r3 + r4
#   54:   mad r1.xyzw, v6.wwww, r7.xyzw, r6.xyzw
        r1 = v6.wwww * r7 + r6
#   55:   mad r2.xyzw, v6.wwww, r8.xyzw, r5.xyzw
        r2 = v6.wwww * r8 + r5
#   56: endif
#   57: dp3 r3.x, r0.xyzx, v1.xyzx
    r3.x = dot(r0.xyz, v1.xyz)
#   58: dp3 r3.y, r1.xyzx, v1.xyzx
    r3.y = dot(r1.xyz, v1.xyz)
#   59: dp3 r3.z, r2.xyzx, v1.xyzx
    r3.z = dot(r2.xyz, v1.xyz)
#   60: dp3 r3.w, r0.xyzx, v2.xyzx
    r3.w = dot(r0.xyz, v2.xyz)
#   61: dp3 r4.x, r1.xyzx, v2.xyzx
    r4.x = dot(r1.xyz, v2.xyz)
#   62: dp3 r4.y, r2.xyzx, v2.xyzx
    r4.y = dot(r2.xyz, v2.xyz)
#   63: add r5.xyz, v0.xyzx, v8.xyzx
    r5.xyz = v0.xyz + v8.xyz
#   64: mov r5.w, l(1.000000)
    r5.w = 1.0
#   65: dp4 r0.x, r0.xyzw, r5.xyzw
    r0.x = dot(r0.xyzw, r5.xyzw)
#   66: dp4 r0.y, r1.xyzw, r5.xyzw
    r0.y = dot(r1.xyzw, r5.xyzw)
#   67: dp4 r0.z, r2.xyzw, r5.xyzw
    r0.z = dot(r2.xyzw, r5.xyzw)
#   68: add r0.xyz, r0.xyzx, v9.xyzx
    r0.xyz = r0.xyz + v9.xyz
    return r0.xyz

def get_texcoord(vid : int) -> vec2:
    global vertex_inputs
    data = vertex_inputs[vid][2:][11:13]
    return vec2(data[0], data[1])

for file in os.listdir("csv"):
    if file.endswith('.csv'):
        filename = file[:-4]
        print(f"Converting {filename}...")
        convert_csv(filename)
        print(f"{filename} converted successfully.")

# vex脚本：
# int count = npoints(0);
# for (int i = 0; i < count / 3; i++)
# {
#     int p0 = i * 3;
#     int p1 = i * 3 + 1;
#     int p2 = i * 3 + 2;
#     addprim(0, "poly", p0, p2, p1);
# }