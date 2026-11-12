package com.wx.convertor

import android.net.Uri
import android.os.Bundle
import android.provider.OpenableColumns
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import java.io.File
import kotlin.concurrent.thread

class MainActivity : ComponentActivity() {

    private var inputUri: Uri? = null
    private var inputName: String = ""
    private var resultZip: File? = null

    private lateinit var pickBtn: Button
    private lateinit var nameEdit: EditText
    private lateinit var convertBtn: Button
    private lateinit var saveBtn: Button
    private lateinit var progress: ProgressBar
    private lateinit var status: TextView
    private lateinit var picked: TextView

    private val pickLauncher =
        registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
            if (uri != null) {
                inputUri = uri
                inputName = displayName(uri)
                picked.text = inputName
                nameEdit.setText(inputName.substringBeforeLast('.') + "_bg")
                convertBtn.isEnabled = true
                saveBtn.isEnabled = false
                resultZip = null
                status.text = ""
            }
        }

    private val saveLauncher =
        registerForActivityResult(ActivityResultContracts.CreateDocument("application/zip")) { uri ->
            val zip = resultZip
            if (uri != null && zip != null) {
                try {
                    contentResolver.openOutputStream(uri)?.use { out ->
                        zip.inputStream().use { it.copyTo(out) }
                    }
                    Toast.makeText(this, "ZIP salvo!", Toast.LENGTH_SHORT).show()
                } catch (e: Exception) {
                    Toast.makeText(this, "Erro ao salvar: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (!Python.isStarted()) Python.start(AndroidPlatform(this))
        buildUi()
    }

    private fun dp(v: Int) = (v * resources.displayMetrics.density).toInt()

    private fun buildUi() {
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(20), dp(32), dp(20), dp(20))
        }
        val title = TextView(this).apply { text = "WxConvertor"; textSize = 26f }
        val sub = TextView(this).apply {
            text = "Converte resource pack Minecraft (Java/Bedrock) para texturas do Blockman GO. A saída é só o .zip."
            setPadding(0, dp(4), 0, dp(20))
        }
        pickBtn = Button(this).apply {
            text = "Escolher ZIP do pack"
            setOnClickListener { pickLauncher.launch(arrayOf("*/*")) }
        }
        picked = TextView(this).apply { text = "Nenhum arquivo escolhido"; setPadding(0, dp(8), 0, dp(12)) }
        nameEdit = EditText(this).apply { hint = "Nome do ZIP de saída"; setSingleLine() }
        convertBtn = Button(this).apply {
            text = "Converter"
            isEnabled = false
            setOnClickListener { startConversion() }
        }
        saveBtn = Button(this).apply {
            text = "Salvar ZIP"
            isEnabled = false
            setOnClickListener { saveLauncher.launch(outputName()) }
        }
        progress = ProgressBar(this).apply { isIndeterminate = true; visibility = View.GONE }
        status = TextView(this).apply { setPadding(0, dp(16), 0, 0); setTextIsSelectable(true) }

        listOf(title, sub, pickBtn, picked, nameEdit, convertBtn, saveBtn, progress, status).forEach {
            root.addView(it, LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))
        }
        setContentView(ScrollView(this).apply { addView(root) })
    }

    private fun displayName(uri: Uri): String {
        contentResolver.query(uri, null, null, null, null)?.use { c ->
            val i = c.getColumnIndex(OpenableColumns.DISPLAY_NAME)
            if (i >= 0 && c.moveToFirst()) return c.getString(i)
        }
        return "pack.zip"
    }

    private fun outputName(): String {
        var n = nameEdit.text.toString().trim().replace(Regex("[\\\\/:*?\"<>|]"), "_")
        if (n.isEmpty()) n = inputName.substringBeforeLast('.') + "_bg"
        if (!n.lowercase().endsWith(".zip")) n += ".zip"
        return n
    }

    private fun prepareReference(): File {
        val dir = File(filesDir, "bg_reference").apply { mkdirs() }
        for (name in assets.list("bg_reference").orEmpty()) {
            val dest = File(dir, name)
            if (!dest.exists()) {
                assets.open("bg_reference/$name").use { i -> dest.outputStream().use { o -> i.copyTo(o) } }
            }
        }
        return dir
    }

    private fun startConversion() {
        val uri = inputUri ?: return
        val outName = outputName()
        convertBtn.isEnabled = false
        pickBtn.isEnabled = false
        saveBtn.isEnabled = false
        progress.visibility = View.VISIBLE
        status.text = "Convertendo..."

        thread {
            var zipPath: String? = null
            val message: String
            try {
                val work = File(cacheDir, "work").apply { deleteRecursively(); mkdirs() }
                val ext = inputName.substringAfterLast('.', "zip")
                val inFile = File(work, "entrada.$ext")
                contentResolver.openInputStream(uri)!!.use { i -> inFile.outputStream().use { o -> i.copyTo(o) } }
                val outDir = File(work, "saida").apply { mkdirs() }
                val ref = prepareReference()

                val res = Python.getInstance().getModule("wx_app")
                    .callAttr("convert", inFile.absolutePath, outDir.absolutePath, outName, ref.absolutePath)
                    .asList()
                zipPath = res[0].toString()
                message = res[1].toString()
                inFile.delete()
            } catch (e: Exception) {
                runOnUiThread { finishUi(null, "Erro: ${e.message}") }
                return@thread
            }
            runOnUiThread { finishUi(zipPath, message) }
        }
    }

    private fun finishUi(zipPath: String?, message: String) {
        progress.visibility = View.GONE
        pickBtn.isEnabled = true
        convertBtn.isEnabled = true
        status.text = message
        if (zipPath != null) {
            resultZip = File(zipPath)
            saveBtn.isEnabled = true
            saveLauncher.launch(outputName())
        }
    }
}
